import React, { useState, useEffect } from 'react';
import axios from "axios";
import { Typography, Paper, Select, MenuItem, TextField, Button, InputLabel, FormControl } from '@mui/material';

const Teste = ({ selectedParada, tiposDeParadaNaoPlanejada, tiposDeParadaPlanejada, onSalvarAlteracoes }) => {
  const [observacao, setObservacao] = useState('');
  const [tipoParada, setTipoParada] = useState('');
  const [paradaID, setParadaID] = useState(-1);
  const [alteracoesFeitas, setAlteracoesFeitas] = useState(false);
  const [tipoSelecionado, setTipoSelecionado] = useState('planejada'); // Novo estado para selecionar entre planejada e não planejada
  const [originalSelectedParada, setOriginalSelectedParada] = useState('');

  // Lógica para exibir os tipos de parada com base no tipo de parada selecionado
  const tiposDisponiveis = tipoSelecionado === 'planejada'
    ? tiposDeParadaPlanejada
    : tiposDeParadaNaoPlanejada;

  // Atualiza os campos com os dados da parada selecionada
  useEffect(() => {
    console.log('tiposDeParadaPlanejada', tiposDeParadaPlanejada);
    console.log('tiposDeParadaNaoPlanejada', tiposDeParadaNaoPlanejada);
    if (selectedParada) {
      setOriginalSelectedParada(selectedParada);
      setObservacao(selectedParada.obs || '');
      setTipoParada(selectedParada.paradaSetupID || ''); // Atualiza com o ID do Setup da parada
      setParadaID(selectedParada.paradaID || ''); // Atualiza com o ID da parada
      setTipoSelecionado(selectedParada.paradaType || '');
      console.log('selectedParada', selectedParada);
    }
  }, [selectedParada]);

  // Funções de manipulação
  const handleObservacaoChange = (event) => {
    setObservacao(event.target.value);
    setAlteracoesFeitas(true);
  };

  const handleTipoParadaChange = (event) => {
    setTipoParada(event.target.value);
    setAlteracoesFeitas(true);
  };

  const handleTipoSelecionadoChange = (event) => {
    setTipoSelecionado(event.target.value); // Atualiza o tipo de parada selecionado
    setAlteracoesFeitas(false); // Reseta o estado de alterações feitas
    setTipoParada(''); // Reseta a escolha do tipo de parada quando mudar entre planejada e não planejada
  };
  
  const handleSalvarAlteracoes = async () => {
    try {
      const payload = {
        user: 'Automático', //selectedParada.user || 'usuario_padrao', // ajuste conforme lógica
        paradas_id: paradaID,
        observacoes: observacao,
      };
  
      let response, delete_response;
      console.log('originalSelectedParada', originalSelectedParada)
      
      if (originalSelectedParada.paradaType == "naoJustificada"){
        console.log("Justificando parada não justificada.");
        if (tipoSelecionado === 'planejada') {
          payload.planned_downtime_id = tipoParada;
          response = await axios.post('http://localhost:8000/create_parada_planejada/', payload);
        } else {
          payload.unplanned_downtime_id = tipoParada;
          response = await axios.post('http://localhost:8000/create_parada_nao_planejada/', payload);
        }
      }
      else if (originalSelectedParada.paradaType == tipoSelecionado) {
        console.log("Update justificação de parada."); 
        //console.log("originalSelectedParada.plannedOrUnplannedID", originalSelectedParada.plannedOrUnplannedID)
        
        if (tipoSelecionado === 'planejada') {
          payload.planned_downtime_id = tipoParada;
          response = await axios.put(`http://localhost:8000/update_parada_planejada/${originalSelectedParada.plannedOrUnplannedID}`, payload);
        } else {
          payload.unplanned_downtime_id = tipoParada;
          response = await axios.put(`http://localhost:8000/update_parada_nao_planejada/${originalSelectedParada.plannedOrUnplannedID}`, payload);
        }
      }
      else{
        console.log("Apagando justificação de parada ",originalSelectedParada.paradaType, " e criação de nova ", tipoSelecionado);
        
        if (tipoSelecionado === 'planejada') {
          payload.planned_downtime_id = tipoParada;
          console.log('change to planejado', payload)
          // deleta não planejada
          delete_response = await axios.delete(`http://localhost:8000/delete_unplanned_downtime/${originalSelectedParada.plannedOrUnplannedID}`);
          // cria planejada
          response = await axios.post('http://localhost:8000/create_parada_planejada/', payload);
        } else {
          payload.unplanned_downtime_id = tipoParada;
          console.log('change to não planejado', payload)
          // deleta planejada
          delete_response = await axios.delete(`http://localhost:8000/delete_planned_downtime/${originalSelectedParada.plannedOrUnplannedID}`);
          // cria não planejada
          response = await axios.post('http://localhost:8000/create_parada_nao_planejada/', payload);
        }
      }
  
      console.log('Resposta do backend:', response?.data);
      onSalvarAlteracoes();
      //setAlteracoesFeitas(false);
      resetarCampos();
  
    } catch (error) {
      console.error('Erro ao salvar parada:', error.response?.data || error.message);
      alert('Erro ao salvar parada');
    }
  };

  const resetarCampos = () => {
    setObservacao('');
    setTipoParada('');
    setParadaID(-1);
    setTipoSelecionado('planejada');
    setOriginalSelectedParada('');
    setAlteracoesFeitas(false);
  };
  

  const handleDescartarAlteracoes = () => {
    setObservacao(selectedParada.obs);
    setTipoParada(selectedParada.paradaSetupID);
    setAlteracoesFeitas(false);
  };

  const checkAndFormatTimes = (startTime, endTime) => {
    const formatDate = (date) => new Date(date).toLocaleString();
    return `${formatDate(startTime)} - ${formatDate(endTime)}`;
  };

  return (
    selectedParada && (
      <div style={{ marginTop: '20px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
        <Typography variant="h4" sx={{ color: 'black', backgroundColor: '#f5f5f5' }}>Detalhes da Parada Selecionada:</Typography>
        <Paper sx={{ padding: '16px', backgroundColor: '#f5f5f5', width: '100%' }}>
          <Typography variant="h6">
            <strong>Horário da Parada: </strong>
            {checkAndFormatTimes(selectedParada.startTime, selectedParada.endTime)}
          </Typography>

          <Typography variant="h6">
            <strong>
              Parada {selectedParada.paradaType === 'planejada' ? 'Planejada' : 'Não Planejada'}
            </strong>
          </Typography>

          {/* Seletores */}
          <div style={{display: 'flex', gap: '30px'}}>
            {/* Seletor para escolher entre Paradas Planejadas ou Não Planejadas */}
            <FormControl fullWidth>
              <InputLabel>Tipo de Parada</InputLabel>
              <Select
                value={tipoSelecionado}
                onChange={handleTipoSelecionadoChange}
                label="Tipo de Parada"
              >
                <MenuItem value="planejada">Planejada</MenuItem>
                <MenuItem value="naoPlanejada">Não Planejada</MenuItem>
              </Select>
            </FormControl>

            {/* Seletor de Tipo de Parada baseado na escolha de Parada Planejada ou Não Planejada */}
            <FormControl fullWidth>
              <InputLabel>Parada</InputLabel>
              <Select
                value={tipoParada}
                onChange={handleTipoParadaChange}
                label=""
                disabled={!tipoSelecionado} // Desativa se não tiver escolhido um tipo de parada
              >
                {tiposDisponiveis.map((tipo) => (
                  <MenuItem key={tipo.id} value={tipo.id}>{tipo.name}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </div>

          <strong>Observações: </strong>
          <TextField
            value={observacao}
            onChange={handleObservacaoChange}
            fullWidth
            multiline
            rows={4}
            variant="outlined"
            placeholder="Digite as observações"
          />

          <div style={{ marginTop: '20px', display: 'flex', gap: '10px' }}>
            <Button
              variant="contained"
              color="primary"
              onClick={handleSalvarAlteracoes}
              disabled={!alteracoesFeitas}
            >
              Salvar Alterações
            </Button>
            <Button
              variant="outlined"
              color="secondary"
              onClick={handleDescartarAlteracoes}
              disabled={!alteracoesFeitas}
            >
              Descartar Alterações
            </Button>
          </div>
        </Paper>

        
      </div>
    )
  );
};

export default Teste;
