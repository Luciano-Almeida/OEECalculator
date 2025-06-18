// src/Componentes/MainContent.jsx
import React from 'react';

import Layout from '../Layout/Layout';
import ApontarParadas from '../Pages/Paradas/ApontarParadas';
import ApontarParadasPopUp from '../Pages/Paradas/ApontarParadasPopUp';
import Dashboard from '../Pages/Dashboard';
import OEEDinamico from '../Pages/OEEDinamico/OEEDinamico';
import OEESearch from '../Pages/OEESearch/OEESearch';
import OEESetup from '../Pages/OEESetup/OEESetup';
import StopTypesManagement from '../Pages/SetupParadas/StopTypesManagement';
import Relatorio from '../Pages/Relatorio';
import MenuParadas from '../Pages/Paradas/MenuParadas';
import TesteOEESetup from '../Pages/OEESetup/TesteOEESetup';
import TrilhaDeAuditoria from '../Pages/TrilhaDeAuditoria/TrilhaDeAuditoria';

import { OEEProvider } from '../context/OEEContext';
import { useAuditoria } from '../hooks/useAuditoria';

function MainContent({ currentPage, setCurrentPage, open, setOpen }) {
  const { registrarAuditoria } = useAuditoria();

  const handleClickOpen = () => setOpen(true);
  const handleClose = () => setOpen(false);

  const registrarAberturaTela = async (nomeTela) => {
    await registrarAuditoria(`TELA ${nomeTela}`.toUpperCase(), "Abertura da tela", "Acesso Permitido");
  };

  const handleMenuClick = (page) => {
    if (page === 'ApontarParadas') {
      handleClickOpen();
    } else {
      setCurrentPage(page);
      setOpen(false);
      registrarAberturaTela(page);
    }
  };

  return (
    <Layout onMenuClick={handleMenuClick}>
      <OEEProvider>
        {currentPage === 'OEEDinamico' && <OEEDinamico />}
        {currentPage === 'Voltar' && <OEEDinamico />}
        {currentPage === 'Paradas' && <ApontarParadas />}
        {currentPage === 'OEESearch' && <OEESearch />}
        {currentPage === 'Relatorio' && <Relatorio />}
        {currentPage === 'OEESetup' && <TesteOEESetup />}
        {currentPage === 'ParadasSetup' && <StopTypesManagement />}
        {currentPage === 'TrilhaDeAuditoria' && <TrilhaDeAuditoria />}

        {currentPage !== 'ApontarParadas' && (
          <ApontarParadasPopUp open={open} onClose={handleClose} />
        )}
      </OEEProvider>
    </Layout>
  );
}

export default MainContent;
