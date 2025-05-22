import { useState } from 'react';

import './App.css';
import Layout from './Layout/Layout';

import ApontarParadas from './Pages/Paradas/ApontarParadas';
import ApontarParadasPopUp from './Pages/Paradas/ApontarParadasPopUp';
import Dashboard from './Pages/Dashboard';

import OEEDinamico from './Pages/OEEDinamico/OEEDinamico';
import OEESearch from './Pages/OEESearch/OEESearch'; 
import OEESetup from './Pages/OEESetup/OEESetup';
import StopTypesManagement from './Pages/SetupParadas/StopTypesManagement';

import Relatorio from './Pages/Relatorio'; // Componente de exemplo para Relatório
import { OEEProvider } from './Components/OEEContext';
import MenuParadas from './Pages/Paradas/MenuParadas';
import TesteOEESetup from './Pages/OEESetup/testeOEESetup';
import TrilhaDeAuditoria from './Pages/TrilhaDeAuditoria/TrilhaDeAuditoria';


//import OEEParadas from './Pages/Paradas/OEEParadas';

function App() {
  // Estado para controlar o componente exibido
  const [currentPage, setCurrentPage] = useState('OEEDinamico');
  const [open, setOpen] = useState(false); // Estado para controlar o pop-up

  // Funções para abrir e fechar o pop-up
  const handleClickOpen = () => {
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
  };

  // Função para mudar a página com base no item do menu
  // Função para mudar a página com base no item do menu
  const handleMenuClick = (page) => {
    if (page === 'ApontarParadas') {
      //setCurrentPage('ApontarParadas'); // Defina a página corretamente
      
      handleClickOpen(); // Abre o pop-up
      //<ApontarParadasPopUp open={open} onClose={handleClose} />
    } else {
      setCurrentPage(page); // Para as outras páginas, navega normalmente
      setOpen(false); // Garante que o pop-up será fechado ao navegar para outra página
    }
  };

  return (
    <Layout onMenuClick={handleMenuClick}>
      {/* Conteúdo principal */}
      <OEEProvider>
        {currentPage === 'OEEDinamico' && <OEEDinamico />}
        {currentPage === 'Voltar' && <OEEDinamico />}
        {currentPage === 'Paradas' && <ApontarParadas />}
        {currentPage === 'OEESearch' && <OEESearch />}
        {currentPage === 'Relatorio' && <Relatorio />}

        {currentPage === 'OEESetup' && <TesteOEESetup />}
        {currentPage === 'ParadasSetup' && <StopTypesManagement />}

        {currentPage === 'TrilhaDeAuditoria' && <TrilhaDeAuditoria />}
        

        {/* Mantém a página atual e abre o pop-up quando necessário */}
        {currentPage !== 'ApontarParadas' && (
          <ApontarParadasPopUp open={open} onClose={handleClose} />
        )}
      </OEEProvider>
    </Layout>
  );
}

export default App;








/*
import { useState, useEffect } from 'react';
import './App.css';
import logoImg from './assets/Logo_Nauta.png';
import botaoRelatorio from './assets/Botao_Relatorio.png';
import botaoVoltar from './assets/Botao_Voltar.png';
import Layout from './Layout/Layout';

function App() {
  const [currentTime, setCurrentTime] = useState('');

  useEffect(() => {
    // Função para atualizar o horário atual
    const updateTime = () => {
      const now = new Date();
      const timeString = now.toLocaleTimeString();
      setCurrentTime(timeString);
    };

    // Atualiza o horário a cada segundo
    const timeInterval = setInterval(updateTime, 1000);

    // Limpeza do intervalo quando o componente for desmontado
    return () => clearInterval(timeInterval);
  }, []);

  return (
    <div className="app-container">
      <div className="main-content">
        <div className="header">
          <img src={logoImg} alt="Logo" className="logo" />
          <h1>Sistema de Pesquisa</h1>
        </div>

        <div className="borda_externa">
          <div className="borda_meio">
            <div className="search-bar">
              <div className="init_production">
                <h3>Data de Início da produção</h3>
              </div>
              <div className="end_production">
                <h3>Data de Término da produção</h3>
              </div>
              <div className="pecas_por_minuto">
                <h3>Tempo de ciclo (pç / min)</h3>
              </div>
              <div className="paradas_planejadas">
                <h3>Paradas planejadas (min)</h3>
              </div>
              <input type="text" placeholder="Pesquisar..." />
              <button onClick={() => setCount(count + 1)}>Pesquisar</button>
            </div>
          </div>
        </div>

        <div className="footer">
          <div>
            <p>Usuário: username</p>
          </div>
          <div>
            <p>Hora: {currentTime}</p>
          </div>
        </div>
      </div>

      <div className="sidebar">
          <div className="menu-item">
            <img src={botaoRelatorio} alt="Ícone 1" />
            <p>Relatório</p>
          </div>
          <div className="menu-item">
            <img src={botaoRelatorio} alt="Ícone 2" />
            <p>Item 2</p>
          </div>
          <div className="menu-item">
            <img src={botaoVoltar} alt="Ícone 3" />
            <p>Voltar</p>
          </div>
      </div>
      
    </div>
  );
}

export default App;


*/