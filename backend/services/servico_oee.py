import asyncio
from datetime import datetime, time, timedelta
import logging
from typing import Dict, Any, List
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.db import get_db
from database.db.conexao_db_externo import get_external_db
import database.crud as crud
from database.models import AutoOEE, OEESetup, DigestData, PlannedDowntimeSetup
import schemas as schemas
from services.servico_data_received import fetch_paradas_between, fetch_digest_data_from_datareceived, fetch_all_digest_data_from_datareceived, get_last_timestamp_from_dataReceived_by_camera_id, get_first_timestamp_from_dataReceived_by_camera_id
import services
from utils import DIAS_SEMANA, obter_status_do_setup

# Logger específico
logger = logging.getLogger("serviço OEE")

def str_para_time(hora_str: str) -> time:
    """Converte string no formato 'HH:MM' para objeto datetime.time."""
    return datetime.strptime(hora_str, '%H:%M').time()

class ServicoOEE:
    def __init__(self, intervalo: float = 60.0, db_external: AsyncSession = None, db: AsyncSession = None):#, db: AsyncSession = Depends(get_db)):      
        self._running = False
        self._memo_interval = intervalo
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
        self.digest_time_control: Dict[int, Any] = {} # digest time control por câmera

        # Adicionando lock por camera_id
        self._locks: Dict[int, asyncio.Lock] = {}

        # variaveis gerais
        self.cameras_disponiveis = []
        self.last_data_received = None
        self.agora = None  # centraliza a hora atual de cada running

    async def iniciar(self):
        logger.info("######### Testando se setups OEE estão corretos ########")
        await self.verificar_setup_antes_de_executar()
        
        logger.info("######### Iniciando variáveis cacheadas... #########")
        # busca todos shifts de todas as câmeras
        await self._listar_setup_por_camera()

        # Para cada câmera
        for camera_id in list(self._cache_setupoee.keys()):
            logger.info(f"Iniciando camera {camera_id}")
            try:
                # Carrega e armazena a configuração de parada planejada da câmera
                await self._carregar_setup_parada_planejada(camera_id)

                # Busca e armazena os últimos registros de digest, parada e auto OEE
                await self._carregar_ultimos_registros(camera_id)

                # Converte e armazena os tempos configurados (digest e parada) como timedelta
                self._carregar_tempos_configurados(camera_id)

                self._locks[camera_id] = asyncio.Lock()
            except Exception as e:
                logger.exception(f"[camera_id:{camera_id}] Erro ao iniciar cache de dados: {e}")
        
        await self.running()

    async def running(self):
        try:
            logger.info("######### RUN Serviço OEE... #########")
            self._running = True

            while self._running:
                logger.info(f"Serviço OEE está rodando...intervalo {self._interval}")
                self.agora = datetime.now()

                # Para cada câmera
                for camera_id in list(self._cache_setupoee.keys()):
                    # lock garante que a função não seja chamada múltiplas vezes simultaneamente.
                    async with self._locks[camera_id]:
                        # read last timestamp from dataReceived
                        self.last_data_received = await get_last_timestamp_from_dataReceived_by_camera_id(db=self.db_external, CAMERA_NAME_ID=camera_id)
                        #intervalo_ate_ultimo_data_received = agora - last_data_received
                        if self.last_data_received is None:
                            logger.warning(f"[camera_id:{camera_id}] Nenhum data_received encontrado.")
                            continue  # ou use um valor padrão como `agora`, ou pule esse ciclo
                        else:
                            intervalo_ate_ultimo_data_received = self.agora - self.last_data_received


                        # DigestTime
                        last_digest = self._cache_digest[camera_id]
                        if last_digest:
                            intervalo_ate_ultimo_digest = self.agora - last_digest
                            self.digest_time_control[camera_id] = intervalo_ate_ultimo_digest - intervalo_ate_ultimo_data_received  #                            
                            
                            # verificar se existe muitos dados antigos e acelerar caso afirmativo
                            if self.digest_time_control[camera_id].total_seconds() > 600: # mais de 10 minutos atrasados
                                self._interval = 2  # acelerando para consumir dados antigos
                            else:
                                self._interval = self._memo_interval
                            
                            # processar dados 
                            if self.digest_time_control[camera_id] > self._digest_time[camera_id]:                                                                
                                await self.process_digest_data(camera_id, start=last_digest)
                        else:
                            await self.process_digest_data(camera_id, start=last_digest)

                        # Parada
                        await self.process_paradaNOVO(camera_id)

                        # AUTOOEE calculado uma vez por dia
                        if self.last_calculated_date != self.agora.date():
                            await self.process_autooee(camera_id)
                            self.last_calculated_date = self.agora.date()

                # Espera um intervalo até a próxima análise        
                await asyncio.sleep(self._interval)
        except asyncio.CancelledError:
            logger.exception("⚠️ Serviço OEE cancelado com Ctrl+C")
            raise  # Muito importante: repassar o cancelamento para o loop principal        
        except Exception as e:
            logger.exception(f"Erro ao rodar serviço OEE: {e}")

    async def parar(self):
        logger.info("Parando serviço de OEE...")
        self._running = False


    # Métodos Pirncipais
    async def verificar_setup_antes_de_executar(self):
        # carregar lista de cameras disponiveis
        await self._listar_cameras()

        # verificar status até setups serem corretamente carregados
        status = await obter_status_do_setup(self.db_session)
        while not status["oee_ready"]:
            status = await obter_status_do_setup(self.db_session, lista_de_cameras=self.cameras_disponiveis)
            logger.warning(f"Setup incompleto. Serviço OEE aguardando configuração da(s) câmera(s) {status['cameras_faltando_setup']}.")          
            # Espera um intervalo até a próxima análise        
            await asyncio.sleep(self._interval)
        

    async def process_digest_data(self, camera_id: int, start: datetime, end: datetime=None):
        """ chama a partir de no mímino um periodo mínimo de self._digest_time[camera_id]
            mas se não hover produção será um período maior
        """        
        if end is None:
            end = datetime.now()  # Se 'end' não for fornecido, usa a data/hora atual

        
        logger.info(f"[camera_id:{camera_id}] Processando digest start {start} end {end}")
        if start is not None:
            if start >= end:
                logger.warning(f"Erro: start não pode ser maior ou igual a end. start: {start}, end: {end}")
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
            resultados = await fetch_all_digest_data_from_datareceived(
                db=self.db_external,
                CAMERA_NAME_ID=camera_id, 
                DIGEST_TIME=self._cache_setupoee[camera_id].digest_time
                )

        for row in resultados:
            # Extrair valores de cada linha de resultado
            lote_id = row[0][0]  # row["LoteId"]  # Ajuste conforme o formato do seu resultado
            camera_name_id = row[0][1]  # row["CameraId"]  # Ajuste conforme o formato do seu resultado
            ok = row[0][2]  # row["total_ok"]
            nok = row[0][3]  # row["total_nok"]
            last_timestamp = row[0][4]

            # Convertendo start_digest e stop_digest para datetime
            start_digest = row[1]
            stop_digest = last_timestamp

            # Chamar a função para criar o registro na tabela DigestData
            await crud.create_digest_data(db=self.db_session, ok=ok, nok=nok, lote_id=lote_id, camera_name_id=camera_name_id,
                                        start_digest=start_digest, stop_digest=stop_digest)
        
            # Atualiza cache
            self._cache_digest[camera_id] = stop_digest
            logger.debug(f"[camera_id:{camera_id}] self._cache_digest[camera_id] {self._cache_digest[camera_id]}")

    async def process_paradaNOVO(self, camera_id: int):
        ultima_analise_de_parada = self._cache_parada[camera_id]
        shifts = self._cache_setupoee[camera_id].shifts
        stop_time = timedelta(seconds=self._cache_setupoee[camera_id].stop_time)  # tempo sem produção considerado como parada

        # colocar isso direto no cache parada
        if ultima_analise_de_parada is None:
            ultima_analise_de_parada = await get_first_timestamp_from_dataReceived_by_camera_id(self.db_external, camera_id)
            if ultima_analise_de_parada is None:
                logger.warning(f"[camera_id:{camera_id}] Nenhuma data inicial encontrada para análise de parada.")
                return
            logger.info(f"[camera_id:{camera_id}] Primeira análise de parada: {ultima_analise_de_parada}")

        agora = self.agora
        data_analisar = ultima_analise_de_parada.date()

        while data_analisar <= agora.date():
            for turno in shifts:
                dias_validos = [DIAS_SEMANA[d] for d in turno['days']]
                if data_analisar.weekday() not in dias_validos:
                    continue

                turno_inicio = datetime.combine(data_analisar, str_para_time(turno['startTime']))
                turno_fim = datetime.combine(data_analisar, str_para_time(turno['endTime']))

                if turno_fim <= ultima_analise_de_parada:
                    logger.debug(f"[camera_id:{camera_id}] Turno já analisado: {turno['name']}, Início: {turno_inicio}, Fim: {turno_fim}")
                    continue  # já analisado

                if turno_inicio > agora:
                    logger.debug(f"[camera_id:{camera_id}] Turno ainda não começou: {turno['name']}, Início: {turno_inicio}, Fim: {turno_fim}")
                    continue  # turno ainda não começou

                logger.debug(f"[camera_id:{camera_id}] ➤ Possível turno completo desde última parada:")
                logger.debug(f"[camera_id:{camera_id}] Início: {turno_inicio}, Fim: {turno_fim}")
                
                if ultima_analise_de_parada < turno_inicio:
                    inicio_de_pesquisa = turno_inicio
                else:
                    inicio_de_pesquisa = ultima_analise_de_parada

                if agora > turno_fim:
                    fim_pesquisa = turno_fim
                elif self.last_data_received > turno_inicio:
                    fim_pesquisa = self.last_data_received
                else:
                    logger.debug(f"[camera_id:{camera_id}] {self.last_data_received} < {turno_inicio} -> continue")
                    continue

                logger.debug(f"[camera_id:{camera_id}] inicio_de_pesquisa {inicio_de_pesquisa}, fim_pesquisa {fim_pesquisa}")
                paradas = await fetch_paradas_between(
                    self.db_external, 
                    inicio_de_pesquisa, 
                    fim_pesquisa, 
                    stop_time, 
                    camera_id
                )
                for parada in paradas:
                    startTime = parada["startTime"]
                    stopTime = parada["stopTime"]
                    camera_name_id = parada["camera_name_id"]
                    intervalo = parada["intervalo"]

                    logger.debug(f"[camera_id:{camera_id}] Parada {startTime} {stopTime}")

                    await self._verificar_parada_planejada(
                        real_inicio=startTime,
                        real_fim=stopTime,
                        camera_id=camera_id
                    )

                    # Atualiza o cache com a última parte do intervalo
                    self._cache_parada[camera_name_id] = stopTime
                    logger.debug(f'[camera_id:{camera_id}]****** ultima_analise_de_parada atualizado {self._cache_parada[camera_name_id]}')


            data_analisar += timedelta(days=1)
               
    async def process_autooee(self, camera_id: int):
        turnos_pendentes = self.verificar_turnos_pendentes(camera_id)
        for turno in turnos_pendentes:
            logger.debug(f"[camera_id:{camera_id}] Turno pendente: {turno}")
            
            oee_data = await services.oee_by_period(
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

        logger.debug(f"[camera_id:{camera_id}] Shifts {shifts}")
        logger.debug(f"[camera_id:{camera_id}] ultimo_auto_oee {ultimo_auto_oee}")

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
                    logger.debug(f"[camera_id:{camera_id}] Ignorando turno {shift['name']} de {inicio_turno} a {fim_turno} pois last_digest ({self._cache_digest[camera_id]}) não está dentro.")
                    continue
                else:
                    logger.debug(f"[camera_id:{camera_id}] Auto OEE de turno {shift['name']} de {inicio_turno} a {fim_turno}")
                    logger.debug(f"[camera_id:{camera_id}] last digest {self._cache_digest[camera_id]}")

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
        #cameras = self._listar_cameras()
     
        for camera_id in self.cameras_disponiveis:
            setup = await crud.get_oee_setup_by_camera_name_id(db=self.db_session, camera_name_id=camera_id)
            self._cache_setupoee[camera_id] = setup
            logger.debug(f"[camera_id:{camera_id}] cacheando setup")
        
    async def _listar_cameras(self) -> List:
            # Retorne a lista de ID's de câmeras do banco
            #return [2]
            cameras_disponiveis = await services.fetch_enderecos_camera(
                self.db_external, nome_inicial="Câmera"
            )

            self.cameras_disponiveis = [item["id"] for item in cameras_disponiveis]
    
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
            logger.warning(f"[camera_id:{camera_id}] Nenhum dado válido encontrado para stop_digest.")

        if last_parada:
            self._cache_parada[camera_id] = last_parada.stop
        else:
            self._cache_parada[camera_id] = None
            logger.warning(f"[camera_id:{camera_id}] Nenhum dado válido encontrado para parada.stop.")

        if last_autooee:
            self._cache_autooee[camera_id] = last_autooee.end
        else:
            self._cache_autooee[camera_id] = None
            logger.warning(f"[camera_id:{camera_id}] Nenhum dado válido encontrado para auto_oee.end.")

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
            logger.debug(f"[camera_id:{camera_id}] planejado_fim {planejado_fim}")

            # Calcula o período dentro do planejado
            dentro_inicio = max(planejado_inicio, real_inicio)
            dentro_fim = min(planejado_fim, real_fim)
            logger.debug(f"[camera_id:{camera_id}] dentro_fim - dentro_inicio {dentro_fim}, {dentro_inicio}")
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
                    logger.debug(f"[camera_id:{camera_id}] cria parada antes do periodo planejado {real_inicio}, {planejado_inicio}") 
                
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
                logger.debug(f"[camera_id:{camera_id}] cria parada e define como planejada {dentro_inicio}, {dentro_inicio}")

                # parada depois do planejado
                if real_fim > planejado_fim:
                    # cria parada antes do periodo planejado
                    new_parada = await crud.create_parada(
                                    db=self.db_session, 
                                    start=planejado_fim, 
                                    stop=real_fim,
                                    camera_name_id=camera_id
                                )
                    logger.debug(f"[camera_id:{camera_id}] parada depois do planejado {planejado_fim}, {real_fim}")
            
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
            logger.debug(f"[camera_id:{camera_id}] Nova parada fora do setup criada {real_inicio}, {real_fim}")

        