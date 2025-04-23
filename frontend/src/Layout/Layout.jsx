import { useState, useEffect } from 'react';

import './Layout.css';
import logoImg from '../assets/Logo_Nauta.png';
import botaoRelatorio from '../assets/Botao_Relatorio.png';
import botaoVoltar from '../assets/Botao_Voltar.png';
import botaoNovo from '../assets/Botao_Novo.png'
import botaoParada from '../assets/Botao_Paradas.png'
import botaoParametros from '../assets/parameters.png'

// Novos Botões
import botaoFundo from '../assets/novos/Botao_Fundo.png'
import botaoOee from '../assets/novos/Botao_OEE.png'
import botaoOeeSetup from '../assets/novos/Botao_OEE_Setup3.png'
import botaoParadas from '../assets/novos/Botao_Paradas3.png' 
import botaoParadaSetup from '../assets/novos/Botao_Parada_Setup.png' 
import botaoConsulta from '../assets/novos/Botao_Consulta.png'

const Layout = ({ children, onMenuClick}) => {
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
      {/* principal */}
      <div className="main-content">
        {/* Barra superior */}
        <div className="header">
          <img src={logoImg} alt="Logo" className="logo" />
          <h1>OEE</h1>
        </div>

        {/* Conteúdo principal */}
        <div className="borda_externa">
          <div className="borda_meio">
            <div className="borda_interna">
              {children}
            </div>
          </div>
        </div>

        {/* Rodapé */}
        <div className="footer">
          <div>
            <p>Usuário: username</p>
          </div>
          <div>
            <p>Hora: {currentTime}</p>
          </div>
        </div>
      </div>

      {/* Menu lateral */}
      <div className="sidebar">
        <div className="menu-item" onClick={() => onMenuClick('OEEDinamico')}>
            <img src={botaoOee} alt="Ícone 2" />
            <p>OEE</p>
        </div>

        {/* 
        <div className="menu-item" onClick={() => onMenuClick('Relatorio')}>
          <img src={botaoRelatorio} alt="Ícone 1" />
          <p>Relatório</p>
        </div>

        <div className="menu-item" onClick={() => onMenuClick('ApontarParadas')}>
          <img src={botaoParada} alt="Ícone 1" />
          <p>Apontar Paradas</p>
        </div>

        */}

        <div className="menu-item" onClick={() => onMenuClick('Paradas')}>
          <img src={botaoParadas} alt="Imagem transparente" className="imagem-maior" />
          <p>Paradas</p>
        </div>

        <div className="menu-item" onClick={() => onMenuClick('OEESearch')}>
            <img src={botaoConsulta} alt="Ícone 2" />
            <p>Consulta</p>
        </div>

        <div className="menu-item" onClick={() => onMenuClick('OEESetup')}>
            <img src={botaoOeeSetup} alt="Ícone 2" />
            <p>OEE Setup</p>
          </div>
        <div className="menu-item" onClick={() => onMenuClick('ParadasSetup')}>
          <img src={botaoParadaSetup} alt="Ícone 3" />
          <p>Paradas Setup</p>
        </div>

        

        <div className="menu-item" onClick={() => onMenuClick('Voltar')}>
          <img src={botaoVoltar} alt="Ícone 4" />
          <p>Voltar</p>
        </div>
      </div>
    </div>
  );
};

export default Layout;
