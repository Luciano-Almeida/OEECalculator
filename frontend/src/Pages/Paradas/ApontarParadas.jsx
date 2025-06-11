import React, { useState, useEffect } from 'react';
import { Select } from 'antd';
import axios from "axios";
import {
  Timeline,
  TimelineItem,
  TimelineSeparator,
  TimelineConnector,
  TimelineContent,
  TimelineOppositeContent
} from '@mui/lab';
import { Paper, Typography, Button, Box } from '@mui/material';
import {
  CheckCircleOutline as CheckCircleOutlineIcon,
  PauseCircleFilled as PauseCircleFilledIcon,
  Error as ErrorIcon
} from '@mui/icons-material';
import TimelineDot from "@mui/lab/TimelineDot";

import { checkAndFormatTimes } from './timeUtils';
import DatePicker from 'react-datepicker'; // Biblioteca de Data

import './ApontarParadas.css';
import Teste from './teste';
import { useDataInicioFim } from '../../Components/useDataInicioFim';


const { Option } = Select;

const ApontarParadas = () => {
  
  /*
  const [paradas, setParadas] = useState([
    { id: 1, startTime: "2025-03-19 10:00:00", endTime: "2025-03-19 10:15:00", paradaType: "planejada", paradaID: 1, paradaName: "Alongamento", obs: "" },
    { id: 2, startTime: "2025-03-19 12:00:00", endTime: "2025-03-19 13:00:00", paradaType: "planejada", paradaID: 2, paradaName: "Almoço", obs: "" },
    { id: 3, startTime: "2025-03-19 14:30:00", endTime: "2025-03-19 14:45:00", paradaType: "naoPlanejada", paradaID: 3, paradaName: "Falha na Máquina", obs: "Falha no processador." },
    { id: 4, startTime: "2025-03-19 15:00:00", endTime: "2025-03-19 15:10:00", paradaType: "naoPlanejada", paradaID: 0, paradaName: "Não justificada", obs: "" },
    { id: 5, startTime: "2025-03-19 15:15:00", endTime: "2025-03-19 15:30:00", paradaType: "planejada", paradaID: 1, paradaName: "Alongamento", obs: "" },
    { id: 6, startTime: "2025-03-19 16:00:00", endTime: "2025-03-19 17:00:00", paradaType: "naoPlanejada", paradaID: 4, paradaName: "Falta de energia", obs: "Falha no sistema de alimentação de energia" },
  ]);

  const [selectedParada, setSelectedParada] = useState(paradas[0]);
  */
  const [cameraId, setCameraId] = useState(Number(import.meta.env.VITE_CAMERA_DEFAULT) || 1);
  //const [fim, setFim] = useState("2025-04-01 17:00:00");
  const { inicio, setInicio, fim, setFim } = useDataInicioFim();
  const [paradas, setParadas] = useState([]);
  const [paradasNaoPlanejadasTypes, setParadasNaoPlanejadasTypes] = useState([]);
  const [paradasPlanejadasTypes, setParadasPlanejadasTypes] = useState([]);
  const [refreshKey, setRefreshKey] = useState(0);
  const [selectedParada, setSelectedParada] = useState("");

  // Carregar as câmeras do arquivo .env
  const cameras = import.meta.env.VITE_CAMERAS ? import.meta.env.VITE_CAMERAS.split(',') : [];

  

  const buscarParadas = async () => {
    if (new Date(inicio) >= new Date(fim)) {
      alert("A data de início deve ser anterior à data de fim.");
      return;
    }

    const response = await axios.get("http://localhost:8000/paradas_com_tipos/", {
      params: {
        camera_name_id: cameraId,
        inicio,
        fim,
      },
    });
    setParadas(response.data);
    console.log("paradas_com_tipos", response.data);
  };

  const handleSalvarAlteracoes = async () => {
    await buscarParadas(); // Atualiza a lista
    setRefreshKey(prev => prev + 1); // << força o React a remontar o componente Teste
  };

  // Função para definir cor e ícone com base no tipo da parada
  const getParadaInfo = (parada) => {
    const time = checkAndFormatTimes(parada.startTime, parada.endTime);
  
    switch (parada.paradaType) {
      case 'planejada':
        return {
          color: 'success',
          text: 'Parada Planejada',
          text2: time,
          icon: <TimelineDot variant="filled" color="success" />,
          style: {
            color: '#2e7d32', // verde escuro
            fontWeight: 'normal',
            fontStyle: 'normal',
          }
        };
      case 'naoPlanejada':
        return {
          color: 'error',
          text: 'Parada Não Planejada',
          text2: time,
          icon: <TimelineDot variant="filled" color="warning" />,
          style: {
            color: '#ed6c02', // laranja
            fontWeight: 'bold',
            fontStyle: 'italic',
          }
        };
      case 'naoJustificada':
        return {
          color: 'warning',
          text: 'Parada Não Justificada',
          text2: time,
          icon: <ErrorIcon color="error" />,
          style: {
            color: '#d32f2f', // vermelho escuro
            fontWeight: 'bold',
            textDecoration: 'underline',
          }
        };
      default:
        return {
          color: 'grey',
          text: 'Desconhecida',
          text2: time,
          icon: <TimelineDot variant="filled" />,
          style: {
            color: '#000'
          }
        };
    }
  };
  
  const fetchParadasNaoPlanejadasSetup = async () => {
    try {
      const response = await axios.get('http://localhost:8000/get_setup_paradas_nao_planejadas/');
      setParadasNaoPlanejadasTypes(response.data);
      console.log('paradasNaoPlanejadasTypes', paradasNaoPlanejadasTypes, response.data);
    } catch (error) {
      console.error("Erro ao carregar paradas não planejadas", error);
    }
  };

  const fetchParadasPlanejadasSetup = async () => {
    try {
      const response = await axios.get('http://localhost:8000/get_setup_paradas_planejadas/');
      setParadasPlanejadasTypes(response.data);
      console.log('paradasPlanejadasTypes', paradasPlanejadasTypes, response.data);
    } catch (error) {
      console.error("Erro ao carregar paradas planejadas", error);
    }
  };
  /*
  useEffect(() => {
    fetchParadasNaoPlanejadasSetup();
    fetchParadasPlanejadasSetup();
    buscarParadas();
    
  }, [])
  */
 
  useEffect(() => {
    fetchParadasNaoPlanejadasSetup();
    fetchParadasPlanejadasSetup();
  }, []);
  
  useEffect(() => {
    if (inicio && fim) {
      buscarParadas();
    }
  }, [inicio, fim]);

  return (
    <div>
        <div style={{ margin: '10px 50px', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '10px', boxShadow: '0px 4px 6px rgba(0, 0, 0, 0.1)' }}>
          <h3 style={{ textAlign: 'center' }}>Pesquisa Paradas</h3>
          <hr style={{ borderColor: '#aaa', width: '95%', marginBottom: '10px' }} />
          <div className="filters" style={{display: 'flex', flexDirection: 'column', gap: '15px'}}>
            <div>
              <label>Período:</label>
              <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
              <label>
                Início:
                <input
                  type="datetime-local"
                  value={inicio.replace(' ', 'T')}
                  onChange={(e) => setInicio(e.target.value.replace('T', ' '))}
                />
              </label>
              <label>
                Fim:
                <input
                  type="datetime-local"
                  value={fim.replace(' ', 'T')}
                  onChange={(e) => setFim(e.target.value.replace('T', ' '))}
                />
              </label>
              <Button variant="contained" color="primary" onClick={buscarParadas}>
                Buscar
              </Button>
              </div>
            </div>
            <div style={{ display: 'flex', gap: '10px' }}>
              <label>Câmera:</label>
              <Select
                  value={cameraId}
                  onChange={(value) => setCameraId(value)}
                >
                  {cameras.map((camera) => (
                    <Option key={camera} value={camera}>
                      {`${camera}`}
                    </Option>
                  ))}
                </Select>
            </div>
          </div>
        </div>


      <div className='ApontandoParadas'>
        <div 
          style={{
            width: '90%',
            maxWidth: '800px',
            height: '610px',
            overflowY: 'auto',
            border: '1px solid #ccc',
            padding: '10px',
            marginTop: '20px',
            borderRadius: '8px',
            backgroundColor: '#f9f9f9',
          }}
        >
          <Timeline sx={{ marginTop: '20px' }}>
            {paradas.map((parada, index) => {
              const { color, text, text2, icon, style } = getParadaInfo(parada);
              return (
                <TimelineItem key={parada.id}>      
                  <TimelineSeparator>
                    {icon}
                    {index < paradas.length - 1 && <TimelineConnector />}
                  </TimelineSeparator>

                  <TimelineContent sx={{ textAlign: 'left' }}
                  >
                    <Button 
                      variant={selectedParada?.id === parada.id ? "contained" : "outlined"} 
                      onClick={() => setSelectedParada(parada)} 
                      sx={{ 
                        textTransform: 'none',
                        backgroundColor: selectedParada?.id === parada.id ? '#e0f7fa' : 'inherit',
                        borderColor: selectedParada?.id === parada.id ? '#0288d1' : undefined,
                        color: selectedParada?.id === parada.id ? '#01579b' : style.color,
                        fontWeight: selectedParada?.id === parada.id ? 'bold' : style.fontWeight,
                        fontStyle: style.fontStyle,
                        textDecoration: style.textDecoration,
                      }}
                    >
                      {parada.paradaName}
                    </Button>

                  </TimelineContent>
                </TimelineItem>
              );
            })}
          </Timeline>
        </div>
        
        {/* Renderiza o componente Teste quando uma parada for selecionada */}
        <div style={{
            width: '-webkit-fill-available',
            maxWidth: '800px',
            height: '610px',
            overflowY: 'auto',
            border: '1px solid #ccc',
            padding: '10px',
            marginTop: '20px',
            borderRadius: '8px',
            backgroundColor: '#f9f9f9',
          }}>
          {selectedParada && <Teste 
                                key={refreshKey}
                                selectedParada={selectedParada} 
                                tiposDeParadaNaoPlanejada={paradasNaoPlanejadasTypes}
                                tiposDeParadaPlanejada={paradasPlanejadasTypes}
                                onSalvarAlteracoes={handleSalvarAlteracoes}
                              />}
        </div>
      </div>
    </div>
  );
};

export default ApontarParadas;

