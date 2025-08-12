import React, { useState, useEffect } from 'react';
import { Button, Select } from 'antd';
import axios from 'axios';
import moment from 'moment';
import DatePicker from 'react-datepicker'; // Biblioteca de Data
import "react-datepicker/dist/react-datepicker.css"; // Importando os estilos do DatePicker

import './OEESearch.css';

import GraficoCustomPieChart2 from '../Graficos/GraficoCustomPieChart2';
import MediasIndicadores from './Analises/MediasIndicadores';
import GraficoLinha from './Analises/GraficoLinha';
import TotalProduzido from './Analises/TotalProduzido';
import DowntimeChart from './Analises/DownTimeChart';
import { useAuditoria } from '../../hooks/useAuditoria';
import { useCameras } from '../../context/CamerasContext';
import ExportarPDF from '../../Components/ExportarPDF'; 
import { useAuth } from '../../context/AuthContext';

const { Option } = Select;

const OEESearch = () => {
  const [oeeData, setOeeData] = useState([]);
  const [startDate, setStartDate] = useState(new Date());
  const [endDate, setEndDate] = useState(new Date());
  const { cameras, cameraDefault } = useCameras();
  const [cameraId, setCameraId] = useState(null);
  const { registrarAuditoria } = useAuditoria();
  const { usuario } = useAuth();

  const registro = async (action, detalhe) => {
    await registrarAuditoria("TELA BUSCA OEE", action, detalhe);
  };

  useEffect(() => {
    if (cameraDefault){
      setCameraId(cameraDefault);
    }
  }, [cameraDefault]);

  const setStartOfDay = (date) => new Date(date.getFullYear(), date.getMonth(), date.getDate(), 0, 0, 0, 0);
  const setEndOfDay = (date) => new Date(date.getFullYear(), date.getMonth(), date.getDate(), 23, 59, 59, 999);

  const fetchData = async () => {
    if (!startDate || !endDate) {
      alert("Por favor, selecione as datas de início e fim.");
      return;
    }

    const pad = (n) => String(n).padStart(2, '0');
    const formatDateTime = (date) => `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;

    const start = formatDateTime(setStartOfDay(startDate));
    const end = formatDateTime(setEndOfDay(endDate));

    try {
      const response = await axios.get("http://localhost:8000/auto_oee/", {
        params: {
          inicio: start,
          fim: end,
          camera_name_id: cameraId,
        },
      });
      setOeeData(response.data);
      registro("Busca OEE", `Busca início ${start} fim ${end} câmera ${cameraId}`);
    } catch (error) {
      console.error("Erro ao buscar dados:", error);
      registro("Busca OEE", `Erro ao buscar dados: ${error}`);
    }
  };

  return (
    <div>
      {/* Botão de exportar PDF */}
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'stretch' }} id="graficos-container">  
        <div style={{ display: 'flex', flexDirection: 'row', justifyContent: 'space-between' }}>
          {/* Pesquisa */}
          <div style={{ display: 'flex', width: '30%', marginLeft: '10px', flexDirection: 'column', justifyContent: 'space-between' }}>
            <div style={{ width: '100%', marginTop: '10px', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '10px', boxShadow: '0px 4px 6px rgba(0, 0, 0, 0.1)' }}>
              <h3 style={{ textAlign: 'center' }}>Pesquisa de OEE</h3>
              <hr style={{ borderColor: '#aaa', width: '95%', marginBottom: '10px' }} />
              <div className="filters" style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
                <div style={{ display: 'flex', flexWrap: 'wrap' }}>
                  <label>Período:</label>
                  <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'flex-start' }}>
                    <DatePicker
                      selected={startDate}
                      onChange={(date) => setStartDate(date)}
                      dateFormat="yyyy-MM-dd"
                      selectsStart
                      startDate={startDate}
                      endDate={endDate}
                      placeholderText="Data de início"
                    />
                    <span style={{ margin: '0 10px' }}>a</span>
                    <DatePicker
                      selected={endDate}
                      onChange={(date) => setEndDate(date)}
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

                {oeeData.length > 0 && (
                  <ExportarPDF 
                    containerId="graficos-container" 
                    cameraName={cameraId && cameras.find(c => c.id === cameraId)?.nome} 
                    Usuario={usuario.nome}
                    Data={oeeData}
                    TypeOfPDF={1}
                  />
                )}
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

      </div>
    </div>
  );
};

export default OEESearch;
