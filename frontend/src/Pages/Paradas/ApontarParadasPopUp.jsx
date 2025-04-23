import React, { useState } from 'react';
import {
  Timeline,
  TimelineItem,
  TimelineSeparator,
  TimelineConnector,
  TimelineContent,
  TimelineOppositeContent
} from '@mui/lab';
import { Paper, Typography, Button, Box, Dialog, DialogActions, DialogContent, DialogTitle, Menu, MenuItem } from '@mui/material';
import {
  CheckCircleOutline as CheckCircleOutlineIcon,
  PauseCircleFilled as PauseCircleFilledIcon,
  Error as ErrorIcon
} from '@mui/icons-material';
import TimelineDot from "@mui/lab/TimelineDot";

import { checkAndFormatTimes } from './timeUtils';

const ApontarParadasPopUp = ({ open, onClose }) => {
  const [selectedParada, setSelectedParada] = useState(null);
  const [menuAnchor, setMenuAnchor] = useState(null);

  const paradas = [
    { id: 1, startTime: "2025-03-19 10:00:00", endTime: "2025-03-19 10:15:00", paradaType: "planejada", paradaID: 1, paradaName: "Alongamento", obs: "" },
    { id: 2, startTime: "2025-03-19 12:00:00", endTime: "2025-03-19 13:00:00", paradaType: "planejada", paradaID: 2, paradaName: "Almoço", obs: "" },
    { id: 3, startTime: "2025-03-19 14:30:00", endTime: "2025-03-19 14:45:00", paradaType: "naoPlanejada", paradaID: 3, paradaName: "Falha na Máquina", obs: "Falha no processador." },
    { id: 4, startTime: "2025-03-19 15:00:00", endTime: "2025-03-19 15:10:00", paradaType: "naoPlanejada", paradaID: 0, paradaName: "Não justificada", obs: "" },
    { id: 5, startTime: "2025-03-19 15:15:00", endTime: "2025-03-19 15:30:00", paradaType: "planejada", paradaID: 1, paradaName: "Alongamento", obs: "" },
    { id: 6, startTime: "2025-03-19 16:00:00", endTime: "2025-03-19 17:00:00", paradaType: "naoPlanejada", paradaID: 4, paradaName: "Falta de energia", obs: "Falha no sistema de alimentação de energia" },
  ];

  // Função para definir cor e ícone com base no tipo da parada
  const getParadaInfo = (parada) => {
    const time = checkAndFormatTimes(parada.startTime, parada.endTime);
    switch (parada.paradaType) {
      case 'planejada':
        return { color: 'success', text: 'Parada Planejada', text2: time, icon: <TimelineDot variant="filled" color="success" /> };
      case 'naoPlanejada':
        if (parada.paradaID === 0) {
          return { color: 'error', text: 'Parada Não Planejada', text2: time, icon: <ErrorIcon variant="filled" color="error" /> };
        } else {
          return { color: 'warning', text: 'Parada Não Planejada', text2: time, icon: <TimelineDot variant="filled" color="warning" /> };
        }
      default:
        return { color: 'default', text: 'Sem Tipo', text2: time, icon: <ErrorIcon color="disabled" /> };
    }
  };

  const handleOpenMenu = (event, parada) => {
    setMenuAnchor(event.currentTarget);
    setSelectedParada(parada);
  };

  const handleCloseMenu = () => {
    setMenuAnchor(null);
  };

  const handleSelectOption = (option) => {
    // Aqui você pode manipular o que acontece quando uma opção é escolhida
    console.log(`Opção selecionada para a parada ${selectedParada.paradaName}:`, option);
    handleCloseMenu();
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>Lista de Paradas</DialogTitle>
      <DialogContent>
        <Timeline sx={{ marginTop: '20px' }}>
          {paradas.map((parada, index) => {
            const { color, text, text2, icon } = getParadaInfo(parada);
            return (
              <TimelineItem key={parada.id}>
                <TimelineOppositeContent sx={{ m: 0, p: 1, color: 'text.primary', textAlign: 'right' }}>
                  <Typography variant="body2">
                    {parada.paradaName ? `${parada.paradaName}` : 'Sem Nome'}
                  </Typography>
                  <Typography variant="body2" sx={{ fontStyle: 'italic' }}>
                    {parada.obs ? `Observação: ${parada.obs}` : 'Sem Observação'}
                  </Typography>
                </TimelineOppositeContent>

                <TimelineSeparator>
                  {icon}
                  {index < paradas.length - 1 && <TimelineConnector />}
                </TimelineSeparator>

                <TimelineContent sx={{ textAlign: 'left' }}>
                  <Paper sx={{ display: 'inline-block', minWidth: 200, padding: '10px', backgroundColor: '#f5f5f5' }}>
                    <Typography variant="h6" sx={{ marginBottom: '12px' }}>{text}</Typography>
                    <Typography variant="h8" sx={{ whiteSpace: 'pre-line', marginTop: '12px', marginBottom: '8px' }}>
                      {text2}
                    </Typography>
                    <Box sx={{ marginTop: '8px' }}>
                      {parada.paradaType === 'naoPlanejada' && (
                        <Button
                          variant="contained"
                          sx={{
                            backgroundColor: color === 'success' ? 'green' : color === 'error' ? 'red' : 'orange',
                            color: 'white',
                            padding: '8px 16px',
                            fontSize: '14px',
                          }}
                          onClick={(e) => handleOpenMenu(e, parada)}
                        >
                          Alterar
                        </Button>
                      )}
                    </Box>
                  </Paper>
                </TimelineContent>
              </TimelineItem>
            );
          })}
        </Timeline>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} color="primary">
          Fechar
        </Button>
      </DialogActions>

      {/* Menu de opções */}
      <Menu
        anchorEl={menuAnchor}
        open={Boolean(menuAnchor)}
        onClose={handleCloseMenu}
      >
        <MenuItem onClick={() => handleSelectOption("Manutenção Corretiva")}>Manutenção Corretiva</MenuItem>
        <MenuItem onClick={() => handleSelectOption("Falta de energia")}>Falta de energia</MenuItem>
        <MenuItem onClick={() => handleSelectOption("Falha na Máquina")}>Falha na Máquina</MenuItem>
      </Menu>
    </Dialog>
  );
};

export default ApontarParadasPopUp;
