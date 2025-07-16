import React, { useState, useEffect } from 'react';
import { Button, Select } from 'antd';
import axios from 'axios';
import moment from 'moment';
import DatePicker from 'react-datepicker'; // Biblioteca de Data
import "react-datepicker/dist/react-datepicker.css"; // Importando os estilos do DatePicker

import './OEESearch.css'

import GraficoCustomPieChart2 from '../Graficos/GraficoCustomPieChart2';
import MediasIndicadores from './Analises/MediasIndicadores';
import GraficoLinha from './Analises/GraficoLinha';
import TotalProduzido from './Analises/TotalProduzido';
import DowntimeChart from './Analises/DownTimeChart';
import { useAuditoria } from '../../hooks/useAuditoria';
import { useCameras } from '../../context/CamerasContext';

const { Option } = Select;

const OEESearch = () => {
  const [oeeData, setOeeData] = useState([]);
  const [startDate, setStartDate] = useState(new Date()); // Estado para a data de início
  const [endDate, setEndDate] = useState(new Date()); // Estado para a data de fim
  //const [cameraId, setCameraId] = useState(Number(import.meta.env.VITE_CAMERA_DEFAULT) || 1); // Estado para o ID da câmera, com valor padrão vindo do .env
  //const [mediaIndicadoresTotalProducao, setMediaIndicadoresTotalProducao] = useState([])
  // Carregar as câmeras do arquivo .env
  //const cameras = import.meta.env.VITE_CAMERAS ? import.meta.env.VITE_CAMERAS.split(',') : [];
  const { cameras, cameraDefault } = useCameras();
  const [cameraId, setCameraId] = useState(null);
  const { registrarAuditoria } = useAuditoria();

  const registro = async (action, detalhe) => {
    await registrarAuditoria("TELA BUSCA OEE", action, detalhe);
  };

  // Define o cameraId quando o contexto carrega
  useEffect(() => {
    if (cameraDefault){
      setCameraId(cameraDefault);
    }
  }, [cameraDefault]);

  const setStartOfDay = (date) => {
    return new Date(date.getFullYear(), date.getMonth(), date.getDate(), 0, 0, 0, 0);
  };
  
  const setEndOfDay = (date) => {
    return new Date(date.getFullYear(), date.getMonth(), date.getDate(), 23, 59, 59, 999);
  };  
  

  // Função para buscar os dados
  const fetchData = async () => {
    if (!startDate || !endDate) {
      alert("Por favor, selecione as datas de início e fim.");
      return;
    }

    const pad = (n) => String(n).padStart(2, '0');
    const formatDateTime = (date) => `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;

    const start =  formatDateTime(setStartOfDay(startDate));
    const end = formatDateTime(setEndOfDay(endDate));

    console.log("Datas formatadas para envio:", start, end);

    try {
      const response = await axios.get("http://localhost:8000/auto_oee/", {
        params: {
          inicio: start,
          fim: end,
          camera_name_id: cameraId,
        },
      });
      setOeeData(response.data);
      console.log("response", response.data);
      registro("Busca OEE", `Busca início ${start} fim ${end} câmera ${cameraId}`);
    } catch (error) {
      console.error("Erro ao buscar dados:", error);
      registro("Busca OEE", `Erro ao buscar dados: ${error}`);
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'stretch' }}>
        
        <div style={{ display: 'flex', flexDirection: 'row', justifyContent: 'space-between' }}>
          {/* Pesquisa */}
          <div style={{ display: 'flex', width: '30%', marginLeft: '10px', flexDirection: 'column', justifyContent: 'space-between' }}>
            <div style={{ width: '100%', marginTop: '10px', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '10px', boxShadow: '0px 4px 6px rgba(0, 0, 0, 0.1)' }}>
              <h3 style={{ textAlign: 'center' }}>Pesquisa de OEE</h3>
              <hr style={{ borderColor: '#aaa', width: '95%', marginBottom: '10px' }} />
              <div className="filters" style={{display: 'flex', flexDirection: 'column', gap: '15px'}}>
                <div style={{display: 'flex', flexWrap: 'wrap'}}>
                  <label>Período:</label>
                  <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'flex-start' }}>
                    <DatePicker
                      selected={startDate}
                      onChange={(date) => {
                        //const adjusted = setStartOfDay(date);
                        setStartDate(date);
                      }} 
                      dateFormat="yyyy-MM-dd"
                      selectsStart
                      startDate={startDate}
                      endDate={endDate}
                      placeholderText="Data de início"
                    />
                    <span style={{ margin: '0 10px' }}>a</span>
                    <DatePicker
                      selected={endDate}
                      onChange={(date) => {
                        //const adjusted = setEndOfDay(date);
                        setEndDate(date);
                      }} // Atualizando a data de fim
                      dateFormat="yyyy-MM-dd"
                      selectsEnd
                      startDate={startDate}
                      endDate={endDate}
                      minDate={startDate} // Não permitir selecionar data de fim anterior à de início
                      placeholderText="Data de fim"
                    />
                  </div>
                </div>
                
                {cameras.length > 1 && (
                  <div style={{ display: 'flex', gap: '10px' }}>
                    <label>Câmera:</label>
                    <Select
                      value={cameraId}
                      onChange={async (value) => {
                        setCameraId(value);
                        await registro("ALTERAÇÃO", `Tipo de câmera alterada: ${value}`);
                      }}
                    >
                      {cameras.map((camera) => (
                        <Option key={camera.id} value={camera.id}>
                          {`${camera.nome}`}
                        </Option>
                      ))}
                    </Select>
                  </div>
                )}
                <Button type="primary" onClick={fetchData}>Buscar</Button>
              </div>
            </div>
          </div>

          {/* médias de OEE */}        
          <MediasIndicadores oeeData={oeeData} />
        </div>

        {/* Total de produção no periodo  */}
        <TotalProduzido oeeData={oeeData} />

        {/* Histórico  ao longo do tempo */}
        <GraficoLinha oeeData={oeeData} />

        {/* Resumo das Paradas */}
        <DowntimeChart oeeData={oeeData} />


        {/* mediana, desvio padrão do OEE 
        <label>Insights: Verificar se há grandes variações ou se os turnos de produção têm desempenhos muito diferentes entre si.</label>*/}

        {/* Comparar turnos -> Identificação de Turnos com Menor Performance         
        <div style={{ width: '100%', marginTop: '10px', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '10px', boxShadow: '0px 4px 6px rgba(0, 0, 0, 0.1)' }}>
          <h3 style={{ textAlign: 'center' }}>Comparação de Turnos </h3>
          <hr style={{ borderColor: '#aaa', width: '95%', marginBottom: '10px' }} />
          <label>Insights: Comparar turnos, Identificação de Turnos com Menor Performance</label>
                        
        </div>
        */}
        
      </div>
    </div>
  );
};

export default OEESearch;
