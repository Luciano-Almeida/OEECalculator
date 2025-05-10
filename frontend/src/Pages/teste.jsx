import React, { useState, useEffect } from 'react';
import axios from "axios";
import { Typography, Paper, Select, MenuItem, TextField, Button, InputLabel, FormControl } from '@mui/material';

const Teste = ({ selectedParada, tiposDeParada, onSalvarAlteracoes }) => {
  const [observacao, setObservacao] = useState('');
  const [tipoParada, setTipoParada] = useState('');
  const [paradaID, setParadaID] = useState(-1);
  const [alteracoesFeitas, setAlteracoesFeitas] = useState(false);

  // Atualiza os campos com os dados da parada selecionada
  useEffect(() => {
    if (selectedParada) {
      setObservacao(selectedParada.obs || '');
      setTipoParada(selectedParada.paradaSetupID || ''); // Atualiza com o ID do Setup da parada
      setParadaID(selectedParada.paradaID || ''); // Atualiza com o ID da parada
      console.log('tipoParada', selectedParada.paradaSetupID);
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
  /*
  const handleSalvarAlteracoes = () => {
    // Envia o objeto com a alteração para o estado pai
    const tipoSelecionado = tiposDeParada.find(tipo => tipo.id === tipoParada);
    onSalvarAlteracoes({
      ...selectedParada,
      obs: observacao,
      paradaID: tipoParada, // Salva o ID da parada selecionada
      paradaName: tipoSelecionado ? tipoSelecionado.name : '', // Salva o nome correspondente ao ID
    });
    setAlteracoesFeitas(false);
  };
  */
  const handleSalvarAlteracoes = async () => {
    try {
      const tipoSelecionado = tiposDeParada.find(tipo => tipo.id === tipoParada);
  
      const payload = {
        user: 'Luciano', //selectedParada.user || 'usuario_padrao', // ajuste conforme sua lógica
        unplanned_downtime_id: tipoParada,
        paradas_id: paradaID,
        observacoes: observacao,
      };
  
      console.log('Enviando payload:', payload);
  
      const response = await axios.post('http://localhost:8000/create_parada_nao_planejada/', payload);
      console.log('Resposta do backend:', response.data);
      /*
      onSalvarAlteracoes({
        ...selectedParada,
        obs: observacao,
        paradaID: tipoParada,
        paradaName: tipoSelecionado ? tipoSelecionado.name : '',
      });
  
      setAlteracoesFeitas(false);
      */
    } catch (error) {
      console.error('Erro ao salvar parada não planejada:', error.response?.data || error.message);
      alert('Erro ao salvar parada não planejada');
    }
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

          <FormControl fullWidth>
            <InputLabel>Tipo de Parada</InputLabel>
            <Select
              value={tipoParada}
              onChange={handleTipoParadaChange}
              label="Tipo de Parada"
            >
              {tiposDeParada.map((tipo) => (
                <MenuItem key={tipo.id} value={tipo.id}>{tipo.name}</MenuItem>
              ))}
            </Select>
          </FormControl>

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
