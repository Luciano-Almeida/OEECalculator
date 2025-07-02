import asyncio
from datetime import datetime, time, timedelta
from typing import Dict, Any, List
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.db import get_db
from database.db.conexao_db_externo import get_external_db
import database.crud as crud
from database.models import AutoOEE, OEESetup, DigestData, PlannedDowntimeSetup
import schemas as schemas
from services.servico_data_received import fetch_paradas_after_init_date, fetch_paradas, fetch_digest_data_from_datareceived, fetch_all_digest_data_from_datareceived, get_last_timestamp_from_dataReceived_by_camera_id
from services import oee_by_period
from utils import DIAS_SEMANA


"""DIAS_SEMANA = {
    'Segunda': 0,
    'Terça': 1,
    'Quarta': 2,
    'Quinta': 3,
    'Sexta': 4,
    'Sábado': 5,
    'Domingo': 6
}"""

def str_para_time(hora_str: str) -> time:
    """Converte string no formato 'HH:MM' para objeto datetime.time."""
    return datetime.strptime(hora_str, '%H:%M').time()

class ServicoOEE:
    def __init__(self, intervalo: float = 60.0, db_external: AsyncSession = None, db: AsyncSession = None):#, db: AsyncSession = Depends(get_db)):      
        self._running = False
        self._interval = intervalo  # segundos entre cada verificação
        self.db_session = db
        self.db_external = db_external
        self.last_calculated_date = None
        
        #self._cache_shifts_por_camera: Dict[int, schemas.Shift]
        self._cache_digest: Dict[int, datetime] = {}
        self._cache_parada: Dict[int, datetime] = {}
        self._cache_autooee: Dict[int, datetime] = {}
        
        self._cache_setupoee: Dict[int, OEESetup] = {}
        self._digest_time: Dict[int, timedelta] = {}
        self._stop_time: Dict[int, timedelta] = {}

        self._cache_setup_parada_planejada: Dict[int, PlannedDowntimeSetup] = {}
        self._inicio_parada_turno: Dict[int, datetime] = {}
        self._oee_atual: Dict[int, Any] = {}  # dados atuais do OEE por shift_id

        # Adicionando lock por camera_id
        self._locks: Dict[int, asyncio.Lock] = {}

        # variaveis gerais
        self.last_data_received = None
        self.agora = None  # centraliza a hora atual de cada running

    async def iniciar(self):
        print("######### Iniciando variáveis cacheadas... #########", flush=True)
        # busca todos shifts de todas as câmeras
        await self._listar_setup_por_camera()

        # Para cada câmera
        for camera_id in list(self._cache_setupoee.keys()):
            print(f"Iniciando camera {camera_id}")
            try:
                # Carrega e armazena a configuração de parada planejada da câmera
                await self._carregar_setup_parada_planejada(camera_id)

                # Busca e armazena os últimos registros de digest, parada e auto OEE
                await self._carregar_ultimos_registros(camera_id)

                # Converte e armazena os tempos configurados (digest e parada) como timedelta
                self._carregar_tempos_configurados(camera_id)

                self._locks[camera_id] = asyncio.Lock()
            except Exception as e:
                print(f"[camera_id:{camera_id}] Erro ao iniciar cache de dados: {e}")
        
        await self.running()

    async def running(self):
        try:
            #logger.info("Iniciando variáveis chached...")
            print("######### RUN Serviço OEE... #########", flush=True)
            self._running = True

            while self._running:
                #logger.info("Serviço OEE está rodando...")
                print(f"Serviço OEE está rodando...intervalo {self._interval}", flush=True)
                self.agora = datetime.now()

                # Para cada câmera
                for camera_id in list(self._cache_setupoee.keys()):
                    # lock garante que a função não seja chamada múltiplas vezes simultaneamente.
                    async with self._locks[camera_id]:
                        print(f"running camera {camera_id}")

                        # read last timestamp from dataReceived
                        self.last_data_received = await get_last_timestamp_from_dataReceived_by_camera_id(db=self.db_external, CAMERA_NAME_ID=camera_id)
                        #intervalo_ate_ultimo_data_received = agora - last_data_received
                        #print("last data_received timestamp", last_data_received)
                        if self.last_data_received is None:
                            print(f"[camera_id:{camera_id}] Nenhum data_received encontrado.")
                            continue  # ou use um valor padrão como `agora`, ou pule esse ciclo
                        else:
                            intervalo_ate_ultimo_data_received = self.agora - self.last_data_received


                        # DigestTime
                        last_digest = self._cache_digest[camera_id]
                        if last_digest:
                            intervalo_ate_ultimo_digest = self.agora - last_digest
                            digest_time_control = intervalo_ate_ultimo_digest - intervalo_ate_ultimo_data_received#
                            if digest_time_control > self._digest_time[camera_id]:                                
                                await self.process_digest_data(camera_id, start=last_digest)
                        else:
                            await self.process_digest_data(camera_id, start=last_digest)

                        # Parada
                        '''last_parada = self._cache_parada[camera_id]
                        if last_parada:
                            intervalo_ate_ultima_parada = agora - last_parada
                            parada_time_control = intervalo_ate_ultima_parada - intervalo_ate_ultimo_data_received
                            if parada_time_control > self._digest_time[camera_id]:
                                await self.process_parada(camera_id, start=last_parada)
                        else:'''
                        await self.process_parada(camera_id)

                        # AUTOOEE calculado uma vez por dia
                        if self.last_calculated_date != self.agora.date():
                            await self.process_autooee(camera_id)
                            self.last_calculated_date = self.agora.date()

                # Espera um intervalo até a próxima análise        
                await asyncio.sleep(self._interval)
        except asyncio.CancelledError:
            print("⚠️ Serviço OEE cancelado com Ctrl+C")
            raise  # Muito importante: repassar o cancelamento para o loop principal        
        except Exception as e:
            print(f"Erro ao rodar serviço OEE: {e}")

    async def parar(self):
        #logger.info("Parando serviço de OEE...")
        print("Parando serviço de OEE...")
        self._running = False


    # Métodos Pirncipais
    async def process_digest_data(self, camera_id: int, start: datetime, end: datetime=None):
        """ chama a partir de no mímino um periodo mínimo de self._digest_time[camera_id]
            mas se não hover produção será um período maior
        """        
        if end is None:
            end = datetime.now()  # Se 'end' não for fornecido, usa a data/hora atual

        
        print(f"processando digest data camera: {camera_id} start {start} end {end}")
        if start is not None:
            if start >= end:
                print(f"Erro: start não pode ser maior ou igual a end. start: {start}, end: {end}")
                return
            resultados = await fetch_digest_data_from_datareceived(
                db=self.db_external, 
                CAMERA_NAME_ID=camera_id,
                DIGEST_TIME=self._cache_setupoee[camera_id].digest_time, 
                START_ANALISE=start, # datetime "'2025-03-24 16:23:00'",
                STOP_ANALISE=end
                )
        else:
            # Verifica se o start está antes do 'end'
            print("aqui")            
            resultados = await fetch_all_digest_data_from_datareceived(
                db=self.db_external,
                CAMERA_NAME_ID=camera_id, 
                DIGEST_TIME=self._cache_setupoee[camera_id].digest_time
                )

        for row in resultados:
            # Extrair valores de cada linha de resultado
            #print('###### row', row)
            lote_id = row[0][0]  # row["LoteId"]  # Ajuste conforme o formato do seu resultado
            camera_name_id = row[0][1]  # row["CameraId"]  # Ajuste conforme o formato do seu resultado
            ok = row[0][2]  # row["total_ok"]
            nok = row[0][3]  # row["total_nok"]
            last_timestamp = row[0][4]

            # Convertendo start_digest e stop_digest para datetime
            #start_digest = datetime.strptime(row[1], "'%Y-%m-%d %H:%M:%S'")  # Format according to the string format
            #stop_digest = datetime.strptime(row[2], "'%Y-%m-%d %H:%M:%S'")  # Same as above
            start_digest = row[1]
            stop_digest = last_timestamp

            # Chamar a função para criar o registro na tabela DigestData
            #async with self.db_session.begin():
            await crud.create_digest_data(db=self.db_session, ok=ok, nok=nok, lote_id=lote_id, camera_name_id=camera_name_id,
                                        start_digest=start_digest, stop_digest=stop_digest)
        
            # Atualiza cache
            self._cache_digest[camera_id] = stop_digest
            #self._cache_digest[camera_id] = last_timestamp
            print("###self._cache_digest[camera_id]", self._cache_digest[camera_id])
            print('last_timestamp', last_timestamp)

    async def process_parada(self, camera_id: int):
        ultima_analise_de_parada = self._cache_parada[camera_id]
        stop_time = timedelta(seconds=self._cache_setupoee[camera_id].stop_time)  # tempo sem produção considerado como parada

        if ultima_analise_de_parada is None:
            print('ultima parada planejada is none')
            #date_test = datetime.strptime("'2025-05-28 12:38:43.176207'".strip("'"), "%Y-%m-%d %H:%M:%S")
            paradas = await fetch_paradas(
                db=self.db_external, 
                PARADA_TIME_STOP=stop_time
                )
        else:
            print("9999999ultima_analise_de_parada", ultima_analise_de_parada)
            paradas = await fetch_paradas_after_init_date(
                db=self.db_external, 
                INIT=ultima_analise_de_parada, 
                PARADA_TIME_STOP=stop_time
                )
            
        for row in paradas:
            startTime = row[0]#.isoformat() if row[0] else None
            stopTime = row[1]#.isoformat() if row[1] else None
            camera_name_id = row[2]
            intervalo = row[3]

            # Obter turnos da câmera
            shifts = self._cache_setupoee[camera_name_id].shifts

            # Dividir parada se cruzar turnos
            partes_parada = await self.dividir_parada_por_turno(startTime, stopTime, shifts)

            for parte in partes_parada:
                await self._verificar_parada_planejada(
                    real_inicio=parte['start'],
                    real_fim=parte['end'],
                    camera_id=camera_name_id
                )

                # Atualiza o cache com a última parte do intervalo
                self._cache_parada[camera_name_id] = parte['end']
                print('****** ultima_analise_de_parada', self._cache_parada[camera_name_id])
        
        await self.verificar_paradas_no_inicio_do_turno(camera_id)

        if not paradas and ultima_analise_de_parada is not None and self.last_data_received is not None:
            # Executa código quando NÃO houver nenhuma parada
            if ultima_analise_de_parada < self.last_data_received:
                intervalo = self.agora - self.last_data_received
                # saber se intervalo até ultima parada é maior que time_stop
                if intervalo >= stop_time:
                    # saber se ultimo data_receiveid é anterior ao dia atual -> se sim salvar parada
                    if self.agora.date() > self.last_data_received.date():
                        print("🟡 Data atual é diferente da última data_received.")
                        print(f"➡️ Salvando parada de {self.last_data_received} até {self.agora} por mudança de dia.")
                        
                        await self._verificar_parada_planejada(
                            real_inicio=self.last_data_received,
                            real_fim=self.agora,
                            camera_id=camera_id
                        )

                        # Atualiza o cache
                        self._cache_parada[camera_id] = self.agora
                        print(f"🆕 Cache de parada atualizado: {self._cache_parada[camera_id]}")

                    else:
                        print("🔄 Mesma data do último data_received. Verificando encerramento de turno...")
                       
                        shifts = self._cache_setupoee[camera_id].shifts
                        encontrou_turno = False
                        for turno in shifts:
                            dias_validos = [DIAS_SEMANA[d] for d in turno['days']]
                            if self.agora.weekday() not in dias_validos:
                                continue

                            turno_inicio = datetime.combine(self.agora.date(), str_para_time(turno['startTime']))
                            turno_fim = datetime.combine(self.agora.date(), str_para_time(turno['endTime']))

                            print(f"🕓 Verificando turno: {turno['name']} - Início: {turno_inicio}, Fim: {turno_fim}")
                            print(f"🔍 Last parada: {ultima_analise_de_parada}, Last data received: {self.last_data_received}, Agora: {self.agora}")
                            
                            if turno_inicio <= self.last_data_received < turno_fim and self.agora >= turno_fim:
                                print("✅ Turno atual terminou. Salvando parada.")
                                await self._verificar_parada_planejada(
                                    real_inicio=self.last_data_received,
                                    real_fim=turno_fim,
                                    camera_id=camera_id
                                )
                                self._cache_parada[camera_id] = turno_fim
                                print(f"🆕 Cache de parada atualizado após fim de turno: {self._cache_parada[camera_id]}")
                                encontrou_turno = True
                                break

                        if not encontrou_turno:
                            print("⚠️ Nenhum turno finalizado identificado para salvar parada.")

    async def verificar_paradas_no_inicio_do_turno(self, camera_id):
        shifts = self._cache_setupoee[camera_id].shifts
        stop_time = timedelta(seconds=self._cache_setupoee[camera_id].stop_time)

        for turno in shifts:
            dias_validos = [DIAS_SEMANA[d] for d in turno['days']]
            if self.agora.weekday() not in dias_validos:
                continue

            turno_inicio = datetime.combine(self.agora.date(), str_para_time(turno['startTime']))
            turno_fim = datetime.combine(self.agora.date(), str_para_time(turno['endTime']))

            if turno_inicio <= self.agora <= turno_fim:
                # Produção ainda não começou no turno
                if self.last_data_received < turno_inicio:
                    tempo_sem_producao = self.agora - turno_inicio
                    if tempo_sem_producao >= stop_time:
                        # Só registra o início uma vez
                        if camera_id not in self._inicio_parada_turno:
                            print(f"⏸️ Turno começou sem produção. Início de possível parada registrado: {turno_inicio}")
                            self._inicio_parada_turno[camera_id] = turno_inicio
                else:
                    # Produção voltou após início do turno sem produção
                    if camera_id in self._inicio_parada_turno:
                        print(f"🟢 Produção retornou. Salvando parada de {self._inicio_parada_turno[camera_id]} até {self.last_data_received}")
                        await self._verificar_parada_planejada(
                            real_inicio=self._inicio_parada_turno[camera_id],
                            real_fim=self.last_data_received,
                            camera_id=camera_id
                        )
                        self._cache_parada[camera_id] = self.last_data_received
                        del self._inicio_parada_turno[camera_id]


    
    def dividir_parada_por_turno(self, inicio: datetime, fim: datetime, shifts: List[Dict]) -> List[Dict[str, datetime]]:
        """
        Divide uma parada que atravessa um ou mais turnos em múltiplas paradas alinhadas aos limites dos turnos.
        Retorna uma lista com dicionários {'start': ..., 'end': ...}
        """
        partes = []
        data = inicio.date()
        while data <= fim.date():
            for turno in shifts:
                dias_validos = [DIAS_SEMANA[d] for d in turno['days']]
                if data.weekday() not in dias_validos:
                    continue

                turno_inicio = datetime.combine(data, str_para_time(turno['startTime']))
                turno_fim = datetime.combine(data, str_para_time(turno['endTime']))

                # Ignora turnos fora do intervalo da parada
                if turno_fim <= inicio or turno_inicio >= fim:
                    continue

                parte_inicio = max(inicio, turno_inicio)
                parte_fim = min(fim, turno_fim)

                if parte_inicio < parte_fim:
                    partes.append({'start': parte_inicio, 'end': parte_fim})
            data += timedelta(days=1)

        # Caso a parada não tenha batido em nenhum turno (fim de semana, etc)
        if not partes:
            partes.append({'start': inicio, 'end': fim})
        return partes


    async def process_autooee(self, camera_id: int):
        turnos_pendentes = self.verificar_turnos_pendentes(camera_id)
        for turno in turnos_pendentes:
            print(f"Turno pendente: {turno}")
            #print(turno['start'], turno['end'], camera_id, self._cache_setupoee[camera_id].line_speed)
            
            oee_data = await oee_by_period(
                                inicio=turno['start'], 
                                fim=turno['end'], 
                                camera_name_id=camera_id, 
                                velocidade_da_linha=self._cache_setupoee[camera_id].line_speed, 
                                db=self.db_session
                                )
            
            #downtime_summary = {"planejadas": 108.82, "nao_planejadas": 85.79, "nao_justificadas": 45.05}
            downtime_summary = await crud.get_resumo_paradas_by_period(
                                db=self.db_session,
                                inicio=turno['start'], 
                                fim=turno['end'], 
                                camera_name_id=camera_id,
                                )
            
            new_autooee = await crud.create_auto_oee(
                                    db=self.db_session, 
                                    init=oee_data['A_Inicio'], 
                                    end=oee_data['A_Fim'], 
                                    camera_name_id=camera_id, 
                                    availability=oee_data['G_Relacao_disponibilidade(F/D)'], 
                                    performance=oee_data['K_Relacao_desempenho(H/J)'], 
                                    quality=oee_data['M_Relacao_qualidade((H-L)/H)'],
                                    oee=oee_data['oee(GxKxM)'], 
                                    total_ok=oee_data['H_Total_pecas_produzidas'] - oee_data['L_Total_pecas_defeituosas'], 
                                    downtime_summary=downtime_summary,
                                    total_not_ok=oee_data['L_Total_pecas_defeituosas']
                                    )
            
            # atualizando cache
            self._cache_autooee[camera_id] = turno['end']

    def verificar_turnos_pendentes(self, camera_id: int) -> List[Dict]:
        """
        Retorna uma lista de turnos (shifts) que ainda não foram registrados
        desde o último AutoOEE salvo até o momento atual.
        """
        turnos_pendentes = []

        if camera_id not in self._cache_setupoee:
            return turnos_pendentes
        elif self._cache_autooee[camera_id] == None:
            """ alterar -> buscar pelo primeiro registro do banco """
            ultimo_auto_oee = datetime(2025, 6, 20, 7, 0, 0)# Exemplo: 25 de fevereiro de 2025, 7:00:00
        else:
            ultimo_auto_oee = self._cache_autooee[camera_id]
        
        shifts = self._cache_setupoee[camera_id].shifts
        agora = datetime.now()

        print('ttttshifts', shifts)
        print('ultimo_auto_oee', ultimo_auto_oee)

        calculando_data = ultimo_auto_oee.date()
        while calculando_data <= agora.date():
            for shift in shifts:
                dias_validos = [DIAS_SEMANA[d] for d in shift['days'] if d in DIAS_SEMANA]
                if calculando_data.weekday() not in dias_validos:
                    continue

                hora_inicio = str_para_time(shift['startTime'])
                hora_fim = str_para_time(shift['endTime'])

                # cria datetime de início e fim do turno
                inicio_turno = datetime.combine(calculando_data, hora_inicio)
                fim_turno = datetime.combine(calculando_data, hora_fim)

                if fim_turno <= ultimo_auto_oee:
                    continue  # já registrado

                # ✅ VERIFICA SE O LAST_DIGEST ESTÁ DENTRO DO TURNO
                # ✅ VERIFICA SE O LAST_DIGEST É MAIOR QUE O TURNO
                #if self._cache_digest[camera_id] is None or not (inicio_turno <= self._cache_digest[camera_id] <= fim_turno):
                if self._cache_digest[camera_id] is None or (self._cache_digest[camera_id] <= fim_turno):
                    print(f"[camera_id:{camera_id}] Ignorando turno {shift['name']} de {inicio_turno} a {fim_turno} pois last_digest ({self._cache_digest[camera_id]}) não está dentro.")
                    continue
                else:
                    print(f"Auto OEE de turno {shift['name']} de {inicio_turno} a {fim_turno}")
                    print(f"last digest {self._cache_digest[camera_id]}")

                if fim_turno <= agora:
                    # turno já passou e ainda não foi registrado
                    turnos_pendentes.append({
                        'camera_id': camera_id,
                        'shift_name': shift['name'],
                        'start': inicio_turno,
                        'end': fim_turno,
                    })

            calculando_data += timedelta(days=1)

        return turnos_pendentes
    

    # Métodos auxiliares
    async def _listar_setup_por_camera(self):
        cameras = self._listar_cameras()
     
        for camera_id in cameras:
            print("camera", camera_id)
            setup = await crud.get_oee_setup_by_camera_name_id(db=self.db_session, camera_name_id=camera_id)
            self._cache_setupoee[camera_id] = setup
        
    def _listar_cameras(self) -> List:
            # Retorne a lista de ID's de câmeras do banco
            return [2]
    
    async def _carregar_setup_parada_planejada(self, camera_id):
        """
        Busca a configuração de parada planejada para a câmera e armazena em cache.
        """
        self._cache_setup_parada_planejada[camera_id] = await crud.get_planned_downtime_setup_by_camera_name_id(
            db=self.db_session, camera_name_id=1
        )

    async def _carregar_ultimos_registros(self, camera_id):
        """
        Busca os últimos registros de digest, parada e auto OEE da câmera.
        Armazena os dados válidos em cache ou gera um aviso se estiverem ausentes.
        """

        # data inicial

        last_digest = await crud.get_last_digest_data_by_camera(db=self.db_session, camera_name_id=camera_id)
        last_parada = await crud.get_last_parada_by_camera(db=self.db_session, camera_name_id=camera_id)
        last_autooee = await crud.get_last_auto_oee_by_camera(db=self.db_session, camera_name_id=camera_id)

        if last_digest:
            self._cache_digest[camera_id] = last_digest.stop_digest
        else:
            self._cache_digest[camera_id] = None
            #logger.warning(f"[{camera_id}] Nenhum dado válido encontrado para stop_digest.")
            print(f"[{camera_id}] Nenhum dado válido encontrado para stop_digest.")

        if last_parada:
            self._cache_parada[camera_id] = last_parada.stop
        else:
            self._cache_parada[camera_id] = None
            #logger.warning(f"[{camera_id}] Nenhum dado válido encontrado para parada.stop.")
            print(f"[{camera_id}] Nenhum dado válido encontrado para parada.stop.")

        if last_autooee:
            self._cache_autooee[camera_id] = last_autooee.end
        else:
            self._cache_autooee[camera_id] = None
            #logger.warning(f"[{camera_id}] Nenhum dado válido encontrado para auto_oee.end.")
            print(f"[{camera_id}] Nenhum dado válido encontrado para auto_oee.end.")

    def _carregar_tempos_configurados(self, camera_id):
        """
        Converte os tempos de digest e parada configurados no setup para objetos timedelta
        e armazena no cache para uso posterior.
        """
        setup = self._cache_setupoee[camera_id]
        self._digest_time[camera_id] = timedelta(seconds=setup.digest_time)
        self._stop_time[camera_id] = timedelta(seconds=setup.stop_time)

    async def _verificar_parada_planejada(self, real_inicio, real_fim, camera_id):
        data_inicio = real_fim.date()
        print('data_inicio', data_inicio)

        for setup in self._cache_setup_parada_planejada[camera_id]:
            # definir data para a parada planejada, para evitar erros de dias diferentes
            planejado_inicio = datetime.combine(data_inicio, setup.start_time) 
            planejado_fim = datetime.combine(data_inicio, setup.stop_time) 
            print('planejado_fim', planejado_fim)
            print('setup', setup)

            # Calcula o período dentro do planejado
            dentro_inicio = max(planejado_inicio, real_inicio)
            dentro_fim = min(planejado_fim, real_fim)
            print('dentro_fim - dentro_inicio', dentro_fim, dentro_inicio)
            # periodo real dentro da parada planejada
            if dentro_fim - dentro_inicio > timedelta(0):
                # parada antes do planejado
                if real_inicio < planejado_inicio:
                    # cria parada antes do periodo planejado
                    new_parada = await crud.create_parada(
                                    db=self.db_session, 
                                    start=real_inicio, 
                                    stop=planejado_inicio,
                                    camera_name_id=camera_id
                                )
                    print('cria parada antes do periodo planejado', real_inicio, planejado_inicio) 
                
                # cria parada e define como planejada
                new_parada = await crud.create_parada(
                                db=self.db_session, 
                                start=dentro_inicio, 
                                stop=dentro_fim,
                                camera_name_id=camera_id
                            )
                new_planed_downtime = await crud.create_planned_downtime(
                                        db=self.db_session,
                                        user="automático",
                                        planned_downtime_id=setup.id,
                                        paradas_id=new_parada.id,
                                        observacoes=""
                                    )
                print('cria parada e define como planejada', dentro_inicio, dentro_inicio)

                # parada depois do planejado
                if real_fim > planejado_fim:
                    # cria parada antes do periodo planejado
                    new_parada = await crud.create_parada(
                                    db=self.db_session, 
                                    start=planejado_fim, 
                                    stop=real_fim,
                                    camera_name_id=camera_id
                                )
                    print('parada depois do planejado', planejado_fim, real_fim)
            
                # sair do loop
                break
        else:
            # esse bloco executa se o loop terminar sem encontrar nenhuma parada planejada
            new_parada = await crud.create_parada(
                            db=self.db_session, 
                            start=real_inicio, 
                            stop=real_fim,
                            camera_name_id=camera_id
                        )
            print("Nova parada fora do setup criada", real_inicio, real_fim)

        