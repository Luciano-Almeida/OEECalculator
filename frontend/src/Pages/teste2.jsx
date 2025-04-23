import React, { useState, useEffect, useRef } from "react";
import './StopTypesManagement.css';

const StopTypesManagement = () => {
  const initialParadasPlanejadasTypes = [
    { id: 1, name: "Manutenção Preventiva", start_time: "", stop_time: "" },
    { id: 2, name: "Almoço", start_time: "12:00", stop_time: "13:00" },
    { id: 3, name: "Alongamento", start_time: "", stop_time: "" },
  ];

  const initialNaoPlanejadasTypes = [
    { id: 1, name: "Manutenção Corretiva" },
    { id: 2, name: "Falta de Energia" },
    { id: 3, name: "Falha na Máquina" },
  ];

  const [paradasPlanejadasTypes, setParadasPlanejadasTypes] = useState(initialParadasPlanejadasTypes);
  const [paradasNaoPlanejadasTypes, setParadasNaoPlanejadasTypes] = useState(initialNaoPlanejadasTypes);

  const [newParadaPlanejadaType, setParadasPlanejadaType] = useState("");
  const [newParadaNaoPlanejadaType, setParadasNaoPlanejadaType] = useState("");
  
  const [selectedPlanejadaItem, setSelectedPlanejadaItem] = useState(null);
  const [selectedNaoPlanejadaItem, setSelectedNaoPlanejadaItem] = useState(null);
  const [editedValues, setEditedValues] = useState({
    name: "",
    startTime: "",
    endTime: ""
  });

  // Refs para evitar conflitos com o clique fora
  const listRefPlanejada = useRef(null);
  const listRefNaoPlanejada = useRef(null);

  const handleAddStopType = () => {
    if (newParadaPlanejadaType.trim()) {
      const newType = {
        id: paradasPlanejadasTypes.length + 1, 
        name: newParadaPlanejadaType,
        category: "planejada",
        startTime: "",
        endTime: "",
      };
      setParadasPlanejadasTypes([...paradasPlanejadasTypes, newType]);
      setParadasPlanejadaType("");
    }
  };

  const handleAddNaoPlanejadaType = () => {
    if (newParadaNaoPlanejadaType.trim()) {
      const newType = {
        id: paradasNaoPlanejadasTypes.length + 1,
        name: newParadaNaoPlanejadaType,
        category: "não planejada",
      };
      setParadasNaoPlanejadasTypes([...paradasNaoPlanejadasTypes, newType]);
      setParadasNaoPlanejadaType("");
    }
  };

  const handleSelectItem = (id, name, category) => {
    if (category === "planejada") {
      const selected = paradasPlanejadasTypes.find((type) => type.id === id);
      // Check if editedValues.name is an empty string before updating
      //if (editedValues.name === '') {
      if (selected && (!selectedPlanejadaItem || selectedPlanejadaItem.id !== id)) {
        setEditedValues({
          name: selected.name,
          startTime: selected.startTime,
          endTime: selected.endTime,
        });
      }
      setSelectedPlanejadaItem({ id, name });
      setSelectedNaoPlanejadaItem(null); // Limpa seleção da outra lista
    } else {
      const selected = paradasNaoPlanejadasTypes.find((type) => type.id === id);
      setEditedValues({ name: selected.name });
      setSelectedNaoPlanejadaItem({ id, name });
      setSelectedPlanejadaItem(null); // Limpa seleção da outra lista
    }
  };

  const handleSaveEdit = () => {
    // Confirmação antes de salvar
    const confirmSave = window.confirm("Você tem certeza que deseja salvar as alterações?");
    if (confirmSave) {
      if (selectedPlanejadaItem) {
        setParadasPlanejadasTypes(paradasPlanejadasTypes.map((type) =>
          type.id === selectedPlanejadaItem.id ? { ...type, ...editedValues } : type
        ));
        setSelectedPlanejadaItem(null);
      } else if (selectedNaoPlanejadaItem) {
        setParadasNaoPlanejadasTypes(paradasNaoPlanejadasTypes.map((type) =>
          type.id === selectedNaoPlanejadaItem.id ? { ...type, name: editedValues.name } : type
        ));
        setSelectedNaoPlanejadaItem(null);
      }
      setEditedValues({ name: "", startTime: "", endTime: "" });
    }
  };
  
  const handleDelete = () => {
    // Confirmação antes de excluir
    const confirmDelete = window.confirm("Você tem certeza que deseja excluir este item?");
    if (confirmDelete) {
      if (selectedPlanejadaItem) {
        setParadasPlanejadasTypes(paradasPlanejadasTypes.filter((type) => type.id !== selectedPlanejadaItem.id));
        setSelectedPlanejadaItem(null);
      } else if (selectedNaoPlanejadaItem) {
        setParadasNaoPlanejadasTypes(paradasNaoPlanejadasTypes.filter((type) => type.id !== selectedNaoPlanejadaItem.id));
        setSelectedNaoPlanejadaItem(null);
      }
      setEditedValues({ name: "", startTime: "", endTime: "" });
    }
  };

  const handleClickOutside = (e) => {
    if (
      listRefPlanejada.current && !listRefPlanejada.current.contains(e.target) &&
      listRefNaoPlanejada.current && !listRefNaoPlanejada.current.contains(e.target)
    ) {
      setSelectedPlanejadaItem(null);
      setSelectedNaoPlanejadaItem(null);
    }
  };

  useEffect(() => {
    document.addEventListener("click", handleClickOutside);
    return () => {
      document.removeEventListener("click", handleClickOutside);
    };
  }, []);

  return (
    <div className="stop-types-management">
      <div className="stop-types-container">
        {/* Coluna para Paradas Planejadas */}
        <div className="stop-types-column" ref={listRefPlanejada}>
          <h2>Paradas Planejadas</h2>
          <ul>
            {paradasPlanejadasTypes.map((type) => (
              <li
                key={type.id}
                onClick={() => handleSelectItem(type.id, type.name, "planejada")}
                style={{ cursor: "pointer", fontWeight: selectedPlanejadaItem?.id === type.id ? 'bold' : 'normal' }}
              >
                {selectedPlanejadaItem?.id === type.id ? (
                  <div>
                    <input
                      type="text"
                      value={editedValues.name}
                      onChange={(e) => setEditedValues({ ...editedValues, name: e.target.value })}
                    />
                    <input
                      type="time"
                      value={editedValues.startTime}
                      onChange={(e) => setEditedValues({ ...editedValues, startTime: e.target.value })}
                    />
                    <input
                      type="time"
                      value={editedValues.endTime}
                      onChange={(e) => setEditedValues({ ...editedValues, endTime: e.target.value })}
                    />
                  </div>
                ) : (
                  <div>
                    {type.name} - {type.start_time} - {type.stop_time}
                  </div>
                )}
              </li>
            ))}
          </ul>

          <div className="separador"></div>
          
          {!selectedPlanejadaItem && (
            <div className="actions">
              <input
                type="text"
                value={newParadaPlanejadaType}
                onChange={(e) => setParadasPlanejadaType(e.target.value)}
                placeholder="Novo tipo de parada planejada"
              />
              <button onClick={handleAddStopType}>Adicionar</button>
            </div>
          )}

          {selectedPlanejadaItem && (
            <div className="actions">
              <button className='save' onClick={handleSaveEdit}>Salvar Edição</button>
              <button className='delete' onClick={handleDelete}>Excluir</button>
            </div>
          )}
        </div>

        {/* Coluna para Paradas Não Planejadas */}
        <div className="stop-types-column" ref={listRefNaoPlanejada}>
          <h2>Paradas Não Planejadas</h2>
          <ul>
            {paradasNaoPlanejadasTypes.map((type) => (
              <li
                key={type.id}
                onClick={() => handleSelectItem(type.id, type.name, "não planejada")}
                style={{ cursor: "pointer", fontWeight: selectedNaoPlanejadaItem?.id === type.id ? 'bold' : 'normal' }}
              >
                {selectedNaoPlanejadaItem?.id === type.id ? (
                  <input
                    type="text"
                    value={editedValues.name}
                    onChange={(e) => setEditedValues({ ...editedValues, name: e.target.value })}
                  />
                ) : (
                  type.name
                )}
              </li>
            ))}
          </ul>

          <div className="separador"></div>
          
          {!selectedNaoPlanejadaItem && (
            <div className="actions">
              <input
                type="text"
                value={newParadaNaoPlanejadaType}
                onChange={(e) => setParadasNaoPlanejadaType(e.target.value)}
                placeholder="Novo tipo de parada não planejada"
              />
              <button onClick={handleAddNaoPlanejadaType}>Adicionar</button>
            </div>
          )}

          {selectedNaoPlanejadaItem && (
            <div className="actions">
              <button className='save' onClick={handleSaveEdit}>Salvar Edição</button>
              <button className='delete' onClick={handleDelete}>Excluir</button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default StopTypesManagement;









----------------------------------------------------
//ApontarParadas
import React, { useState, useEffect } from 'react';
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
  

  const [paradas, setParadas] = useState([
    { id: 1, startTime: "2025-03-19 10:00:00", endTime: "2025-03-19 10:15:00", paradaType: "planejada", paradaID: 1, paradaName: "Alongamento", obs: "" },
    { id: 2, startTime: "2025-03-19 12:00:00", endTime: "2025-03-19 13:00:00", paradaType: "planejada", paradaID: 2, paradaName: "Almoço", obs: "" },
    { id: 3, startTime: "2025-03-19 14:30:00", endTime: "2025-03-19 14:45:00", paradaType: "naoPlanejada", paradaID: 3, paradaName: "Falha na Máquina", obs: "Falha no processador." },
    { id: 4, startTime: "2025-03-19 15:00:00", endTime: "2025-03-19 15:10:00", paradaType: "naoPlanejada", paradaID: 0, paradaName: "Não justificada", obs: "" },
    { id: 5, startTime: "2025-03-19 15:15:00", endTime: "2025-03-19 15:30:00", paradaType: "planejada", paradaID: 1, paradaName: "Alongamento", obs: "" },
    { id: 6, startTime: "2025-03-19 16:00:00", endTime: "2025-03-19 17:00:00", paradaType: "naoPlanejada", paradaID: 4, paradaName: "Falta de energia", obs: "Falha no sistema de alimentação de energia" },
  ]);

  const [selectedParada, setSelectedParada] = useState(paradas[5]);


  // Função para definir cor e ícone com base no tipo da parada
  const getParadaInfo = (parada) => {
    const time = checkAndFormatTimes(parada.startTime, parada.endTime);
    switch (parada.paradaType) {
      case 'planejada':
        return { color: 'success', text: 'Parada Planejada', text2: time, icon: <TimelineDot variant="filled" color="success"/> };
      case 'naoPlanejada':
        if (parada.paradaID === 0) {
          return { color: 'error', text: 'Parada Não Planejada', text2: time, icon: <ErrorIcon variant="filled" color="error" /> };
        } else {
          return { color: 'warning', text: 'Parada Não Planejada', text2: time, icon: <TimelineDot variant="filled" color="warning" /> };
        }
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
    setSelectedParada(alterada);  // Atualiza a parada selecionada no estado
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
                              tiposDeParada={tiposDeParada}
                              onSalvarAlteracoes={handleSalvarAlteracoes}
                            />}
      </div>
    </div>
  );
};

export default ApontarParadas;


