import asyncio
from datetime import datetime, time, timedelta
from typing import Dict, Any, List
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.db import get_db
import database.crud as crud
from database.models import AutoOEE, OEESetup, DigestData, PlannedDowntimeSetup
import schemas as schemas
from services.servico_data_received import fetch_digest_data_from_datareceived, fetch_all_digest_data_from_datareceived, get_last_timestamp_from_dataReceived_by_camera_id
from services import oee_by_period


DIAS_SEMANA = {
    'Segunda': 0,
    'Terça': 1,
    'Quarta': 2,
    'Quinta': 3,
    'Sexta': 4,
    'Sábado': 5,
    'Domingo': 6
}

def str_para_time(hora_str: str) -> time:
    """Converte string no formato 'HH:MM' para objeto datetime.time."""
    return datetime.strptime(hora_str, '%H:%M').time()

class ServicoOEE:
    def __init__(self, intervalo: float = 10.0, db: AsyncSession = None):#, db: AsyncSession = Depends(get_db)):      
        self._running = False
        self._interval = intervalo  # segundos entre cada verificação
        self.db_session = db
        self.last_calculated_date = None
        
        #self._cache_shifts_por_camera: Dict[int, schemas.Shift]
        self._cache_digest: Dict[int, datetime] = {}
        self._cache_parada: Dict[int, datetime] = {}
        self._cache_autooee: Dict[int, datetime] = {}
        
        self._cache_setupoee: Dict[int, OEESetup] = {}
        self._digest_time: Dict[int, timedelta] = {}
        self._stop_time: Dict[int, timedelta] = {}

        self._cache_setup_parada_planejada: Dict[int, PlannedDowntimeSetup] = {}

        self._oee_atual: Dict[int, Any] = {}  # dados atuais do OEE por shift_id

        # Adicionando lock por camera_id
        self._locks: Dict[int, asyncio.Lock] = {}

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
        
        #await self.running()

    async def running(self):
        try:
            #logger.info("Iniciando variáveis chached...")
            print("######### RUN Serviço OEE... #########", flush=True)
            self._running = True

            while self._running:
                #logger.info("Serviço OEE está rodando...")
                print(f"Serviço OEE está rodando...intervalo {self._interval}", flush=True)
                agora = datetime.now()

                # Para cada câmera
                for camera_id in list(self._cache_setupoee.keys()):
                    # lock garante que a função não seja chamada múltiplas vezes simultaneamente.
                    async with self._locks[camera_id]:
                        print(f"running camera {camera_id}")

                        # read last timestamp from dataReceived
                        last_data_received = get_last_timestamp_from_dataReceived_by_camera_id(camera_id)
                        intervalo_ate_ultimo_data_received = agora - last_data_received
                        #print("last data_received timestamp", last_data_received)


                        # DigestTime
                        last_digest = self._cache_digest[camera_id]
                        if last_digest:
                            intervalo_ate_ultimo_digest = agora - last_digest
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
                        #await self.process_parada(camera_id)

                        # AUTOOEE calculado uma vez por dia
                        #if self.last_calculated_date != agora.date():
                        #    await self.process_autooee(camera_id)
                        #    self.last_calculated_date = agora.date()
                    
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
    async def process_digest_data(self, camera_id: int, start: datetime, end=datetime.now()):
        """ chama a partir de no mímino um periodo mínimo de self._digest_time[camera_id]
            mas se não hover produção será um período maior
        """        
        print(f"processando digest data camera: {camera_id} start {start} end {end}")
        if start != None:
            resultados = await fetch_digest_data_from_datareceived(
                CAMERA_NAME_ID=camera_id,
                DIGEST_TIME=self._cache_setupoee[camera_id].digest_time, 
                START_ANALISE=start, # datetime "'2025-03-24 16:23:00'",
                STOP_ANALISE=end
                )
        else:
            resultados = await fetch_all_digest_data_from_datareceived(
                CAMERA_NAME_ID=camera_id, 
                DIGEST_TIME=self._cache_setupoee[camera_id].digest_time
                )

        for row in resultados:
            # Extrair valores de cada linha de resultado
            print('###### row', row)
            lote_id = row[0][0]  # row["LoteId"]  # Ajuste conforme o formato do seu resultado
            camera_name_id = row[0][1]  # row["CameraId"]  # Ajuste conforme o formato do seu resultado
            ok = row[0][2]  # row["total_ok"]
            nok = row[0][3]  # row["total_nok"]
            # Convertendo start_digest e stop_digest para datetime
            start_digest = datetime.strptime(row[1], "'%Y-%m-%d %H:%M:%S'")  # Format according to the string format
            stop_digest = datetime.strptime(row[2], "'%Y-%m-%d %H:%M:%S'")  # Same as above

            # Chamar a função para criar o registro na tabela DigestData
            #async with self.db_session.begin():
            await crud.create_digest_data(db=self.db_session, ok=ok, nok=nok, lote_id=lote_id, camera_name_id=camera_name_id,
                                        start_digest=start_digest, stop_digest=stop_digest)
        
            # Atualiza cache
            self._cache_digest[camera_id] = stop_digest
            print("###self._cache_digest[camera_id]", self._cache_digest[camera_id])

    async def process_parada(self, camera_id: int):
        ultima_analise_de_parada = self._cache_parada[camera_id]
        stop_time = timedelta(seconds=self._cache_setupoee[camera_id].stop_time)  # tempo sem produção considerado como parada
        print('stop_time', stop_time)
        digest = []
        if ultima_analise_de_parada is None:
            print("!!!!!!!!!ultima_analise_de_parada", ultima_analise_de_parada)
            digest = await crud.get_digest_data_by_camera_name_id(
                db=self.db_session, 
                camera_name_id=camera_id
            )
        else:
            print("9999999ultima_analise_de_parada", ultima_analise_de_parada)
            digest = await crud.get_digest_data_filtered_by_stop_and_cameraId(
                db=self.db_session,
                fim=ultima_analise_de_parada,
                camera_name_id=camera_id
            )

        
        if digest:
            for i in range(1, len(digest)):
                difference_between_digest = digest[i].start_digest - digest[i-1].stop_digest
                if difference_between_digest > stop_time:
                    # Verificar se a nova parada é do tipo planejada
                    await self._verificar_parada_planejada(
                        real_inicio=digest[i-1].stop_digest, 
                        real_fim=digest[i].start_digest, 
                        camera_id=camera_id
                    )

            # atualizar cache
            self._cache_parada[camera_id] = digest[-1].stop_digest
            print('****** ultima_analise_de_parada', self._cache_parada[camera_id])
        else:
            print('¨¨¨¨¨¨ ultima_analise_de_parada', ultima_analise_de_parada)

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
                                    quality=oee_data['M_Relacao_qualidade(H-(L/H))'],
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
        elif camera_id not in self._cache_autooee:# or camera_id not in self._cache_setupoee:
            ultimo_auto_oee: datetime = datetime(2025, 3, 13, 7, 0, 0)# Exemplo: 25 de fevereiro de 2025, 7:00:00
        else:
            ultimo_auto_oee: datetime = self._cache_autooee[camera_id]
        
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
            return [1]
    
    async def _carregar_setup_parada_planejada(self, camera_id):
        """
        Busca a configuração de parada planejada para a câmera e armazena em cache.
        """
        self._cache_setup_parada_planejada[camera_id] = await crud.get_planned_downtime_setup_by_camera_name_id(
            db=self.db_session, camera_name_id=camera_id
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

        for setup in self._cache_setup_parada_planejada[camera_id]:
            # definir data para a parada planejada, para evitar erros de dias diferentes
            planejado_inicio = datetime.combine(data_inicio, setup.start_time) 
            planejado_fim = datetime.combine(data_inicio, setup.stop_time) 
            print('planejado_fim', planejado_fim)

            # Calcula o período dentro do planejado
            dentro_inicio = max(planejado_inicio, real_inicio)
            dentro_fim = min(planejado_fim, real_fim)

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
                
                # parada depois do planejado
                if real_fim > planejado_fim:
                    # cria parada antes do periodo planejado
                    new_parada = await crud.create_parada(
                                    db=self.db_session, 
                                    start=planejado_fim, 
                                    stop=real_fim,
                                    camera_name_id=camera_id
                                )
            
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

        