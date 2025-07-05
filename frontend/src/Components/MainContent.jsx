// src/Componentes/MainContent.jsx
import React from 'react';
import { useState, useEffect } from 'react';

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
import StatusSetup from '../Pages/Status/StatusSetup';

function MainContent({ currentPage, setCurrentPage, isOeeReady, reviewStatus, camerasFaltandoSetup }) {
  const { registrarAuditoria } = useAuditoria();

  const registrarAberturaTela = async (nomeTela) => {
    await registrarAuditoria(`TELA ${nomeTela}`.toUpperCase(), "Abertura da tela", "Acesso Permitido");
  };

  useEffect(() => {
    console.log('chamando useeffect isOeeReady', isOeeReady)
    if (isOeeReady === false) {
      setCurrentPage('CheckStatusSetup');
    }
    else {
      setCurrentPage('OEEDinamico');
    }
  }, [isOeeReady]);

  const handleMenuClick = (page) => {
    setCurrentPage(page);
    registrarAberturaTela(page);
  };
  

  const renderPageBasedOnOeeStatus = () => {
    if (isOeeReady === false) {
      //return <StatusSetup onReviewStatus={reviewStatus} />;
      return (
        <>
          {currentPage === 'CheckStatusSetup' && <StatusSetup onReviewStatus={reviewStatus} camerasFaltandoSetup={camerasFaltandoSetup} />}
          {currentPage === 'OEESetup' && <TesteOEESetup />}
          {currentPage === 'ParadasSetup' && <StopTypesManagement />}
        </>
      )
    }

    if (isOeeReady === true) {
      return (
        <>
          {currentPage === 'OEEDinamico' && <OEEDinamico />}
          {currentPage === 'Paradas' && <ApontarParadas />}
          {currentPage === 'OEESearch' && <OEESearch />}
          {currentPage === 'Relatorio' && <Relatorio />}
          {currentPage === 'OEESetup' && <TesteOEESetup />}
          {currentPage === 'ParadasSetup' && <StopTypesManagement />}
          {currentPage === 'TrilhaDeAuditoria' && <TrilhaDeAuditoria />}
        </>
      );
    }

    // Se isOeeReady ainda for null (ex: erro), retorna algo padrão ou nada
    return <div>Erro ao carregar status.</div>;
  };

  return (
    <Layout onMenuClick={handleMenuClick} isOeeReady={isOeeReady}>
      <OEEProvider>
        {renderPageBasedOnOeeStatus()}
      </OEEProvider>
    </Layout>
  );
}

export default MainContent;
