// src/components/MenuComponent.jsx
import { useState } from 'react';
import ApontarParadas from './ApontarParadas';
import StopTypesManagement from '../SetupParadas/StopTypesManagement';
import './MenuParadas.css';  // Importa o CSS para o estilo dos botões

import TimelineComponente from './ApontarParadasPopUp';
import Teste from '../teste';
import ParadasSearch from '../teste3';


const MenuParadas = () => {
  const [activeTab, setActiveTab] = useState('apontarParadas');

  const renderContent = () => {
    if (activeTab === 'apontarParadas') {
      return <ApontarParadas />;
    } else if (activeTab === 'tiposParadas') {
      return <StopTypesManagement />;
    } else if (activeTab === 'timeline') {
      return <TimelineComponente />;
    } else if (activeTab === 'teste') {
      return <Teste />;
    } else if (activeTab === 'ParadasSearch') {
      return <ParadasSearch />;
    } 
  };

  return (
    <div>
      <div className='menuParadas'>
        <button onClick={() => setActiveTab('apontarParadas')}>Apontar Paradas</button>
        <button onClick={() => setActiveTab('tiposParadas')}>Tipos de Paradas</button>
        <button onClick={() => setActiveTab('teste')}>Teste</button>
        <button onClick={() => setActiveTab('ParadasSearch')}>ParadasSearch</button>
      </div>
      <div>
        {renderContent()}
      </div>
    </div>
  );
};

export default MenuParadas;
