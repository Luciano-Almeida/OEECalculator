import React, { useState, useEffect } from 'react';
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

import './ApontarParadas.css'
import Teste from '../teste';

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
  const [cameraId, setCameraId] = useState(1);
  const [inicio, setInicio] = useState('2025-03-14 08:00:00');
  const [fim, setFim] = useState("2025-04-01 17:00:00");
  const [paradas, setParadas] = useState([]);
  const [paradasNaoPlanejadasTypes, setParadasNaoPlanejadasTypes] = useState([]);
  const [paradasPlanejadasTypes, setParadasPlanejadasTypes] = useState([
    {id: 1, name: 'Alongamento'},
    {id: 1, name: 'Almoço'},
    ]);


  const buscarParadas = async () => {
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

  const [selectedParada, setSelectedParada] = useState("");

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
  /*
  const getParadaInfo = (parada) => {
    const time = checkAndFormatTimes(parada.startTime, parada.endTime);
    switch (parada.paradaType) {
      case 'planejada':
        return { color: 'success', text: 'Parada Planejada', text2: time, icon: <TimelineDot variant="filled" color="success"/> };
      case 'naoPlanejada':
        return { color: 'error', text: 'Parada Não Planejada', text2: time, icon: <TimelineDot variant="filled" color="warning" /> };
      case 'naoJustificada':
        return { color: 'warning', text: 'Parada Não Planejada', text2: time, icon: <ErrorIcon variant="filled" color="error" /> };
    }
  };
  */

  /*
  const paradasNaoPlanejadasTypes = [
    "Manutenção Corretiva",
    "Falta de energia",
    "Falha na Máquina"
  ];
  */

  
  const fetchParadasNaoPlanejadasSetup = async () => {
    try {
      const response = await axios.get('http://localhost:8000/get_setup_paradas_nao_planejadas/');
      setParadasNaoPlanejadasTypes(response.data);
      console.log('paradasNaoPlanejadasTypes', paradasNaoPlanejadasTypes, response.data);
    } catch (error) {
      console.error("Erro ao carregar paradas não planejadas", error);
    }
  };

  const handleSalvarAlteracoes = (alterada) => {
    setParadas((prevParadas) =>
      prevParadas.map((parada) =>
        parada.id === alterada.id ? { ...parada, obs: alterada.obs, paradaName: alterada.paradaName } : parada
      )
    );
    setSelectedParada(alterada);  // Atualiza a parada selecionada no estado
  };

  useEffect(() => {
    fetchParadasNaoPlanejadasSetup();
    buscarParadas();
    
  }, [])

  return (
    <div className='ApontandoParadas'>
      {/* 
      <div>
        <h2>Buscar Paradas</h2>
        <input
          type="number"
          placeholder="Camera ID"
          value={cameraId}
          onChange={(e) => setCameraId(e.target.value)}
        />
        <input
          type="datetime-local"
          value={inicio}
          onChange={(e) => setInicio(e.target.value)}
        />
        <input
          type="datetime-local"
          value={fim}
          onChange={(e) => setFim(e.target.value)}
        />
        <button onClick={buscarParadas}>Buscar</button>
      </div>
      */}

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
                    variant="outlined" 
                    onClick={() => setSelectedParada(parada)} 
                    sx={{ 
                      textTransform: 'none',
                      ...style  // <-- aplica cor, fontWeight, etc
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
                              selectedParada={selectedParada} 
                              tiposDeParada={paradasNaoPlanejadasTypes}
                              onSalvarAlteracoes={handleSalvarAlteracoes}
                            />}
      </div>
    </div>
  );
};

export default ApontarParadas;




/*
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  Timeline,
  TimelineItem,
  TimelineSeparator,
  TimelineConnector,
  TimelineContent,
  TimelineOppositeContent,
  TimelineDot
} from '@mui/lab';
import { Paper, Typography, Button, Box } from '@mui/material';
import { Error as ErrorIcon } from '@mui/icons-material';
import { checkAndFormatTimes } from './timeUtils';
import './ApontarParadas.css';
import Teste from '../teste';

START_ANALISE='2025-03-13 08:00:00'; //,#"'2025-03-24 16:23:00'",
STOP_ANALISE = '2025-03-15 13:00:00'; //#"'2025-03-24 19:00:00'"

const ApontarParadas = () => {
  const [paradas, setParadas] = useState([]);
  const [selectedParada, setSelectedParada] = useState(null);

  

  useEffect(() => {
    const fetchParadas = async () => {
      try {
        const response = await axios.get('http://localhost:8000/paradas/');
        setParadas(response.data);  // <-- Atualiza o estado com os dados do backend
        setSelectedParada(response.data[0] || null);  // opcional: define a primeira como selecionada
        console.log("paradas return", response.data);
      } catch (error) {
        console.error("Erro ao carregar as paradas:", error);
      }
    };

    fetchParadas();
  }, []);

  const getParadaInfo = (parada) => {
    const time = checkAndFormatTimes(parada.startTime, parada.endTime);
    switch (parada.paradaType) {
      case 'planejada':
        return { color: 'success', text: 'Parada Planejada', text2: time, icon: <TimelineDot variant="filled" color="success" /> };
      case 'naoPlanejada':
        if (parada.paradaID === 0) {
          return { color: 'error', text: 'Parada Não Planejada', text2: time, icon: <ErrorIcon color="error" /> };
        } else {
          return { color: 'warning', text: 'Parada Não Planejada', text2: time, icon: <TimelineDot variant="filled" color="warning" /> };
        }
      default:
        return { color: 'grey', text: 'Desconhecida', text2: time, icon: <TimelineDot variant="filled" /> };
    }
  };

  const tiposDeParada = [
    "Manutenção Corretiva",
    "Falta de energia",
    "Falha na Máquina"
  ];

  const handleSalvarAlteracoes = (alterada) => {
    setParadas((prevParadas) =>
      prevParadas.map((parada) =>
        parada.id === alterada.id ? { ...parada, obs: alterada.obs, paradaName: alterada.paradaName } : parada
      )
    );
    setSelectedParada(alterada);
  };

  return (
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
            const { color, text, text2, icon } = getParadaInfo(parada);
            return (
              <TimelineItem key={parada.id}>      
                <TimelineSeparator>
                  {icon}
                  {index < paradas.length - 1 && <TimelineConnector />}
                </TimelineSeparator>

                <TimelineContent sx={{ textAlign: 'left' }}>
                  <Button 
                    variant="outlined" 
                    onClick={() => setSelectedParada(parada)} 
                    sx={{ textTransform: 'none' }}
                  >
                    {parada.paradaName}
                  </Button>
                </TimelineContent>
              </TimelineItem>
            );
          })}
        </Timeline>
      </div>

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
                              selectedParada={selectedParada} 
                              tiposDeParada={tiposDeParada}
                              onSalvarAlteracoes={handleSalvarAlteracoes}
                            />}
      </div>
    </div>
  );
};

export default ApontarParadas;
*/
