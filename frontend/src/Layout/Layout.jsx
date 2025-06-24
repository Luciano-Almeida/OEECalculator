import { useState, useEffect } from 'react';

import './Layout.css';
import logoImg from '../assets/Logo_Nauta.png';
import botaoRelatorio from '../assets/Botao_Relatorio.png';
import botaoVoltar from '../assets/Botao_Voltar.png';
import botaoNovo from '../assets/Botao_Novo.png'
import botaoParada from '../assets/Botao_Paradas.png'
import botaoParametros from '../assets/parameters.png'

// Novos Botões
import botaoAuditoria from '../assets/novos/Botao_Auditoria.png'
import botaoFundo from '../assets/novos/Botao_Fundo.png'
import botaoOee from '../assets/novos/Botao_OEE.png'
import botaoOeeSetup from '../assets/novos/Botao_OEE_Setup3.png'
import botaoParadas from '../assets/novos/Botao_Paradas3.png' 
import botaoParadaSetup from '../assets/novos/Botao_Parada_Setup.png' 
import botaoConsulta from '../assets/novos/Botao_Consulta.png'
import { useAuth } from '../context/AuthContext';

const MENU_ITEMS = [
  {
    label: 'OEE',
    icon: botaoOee,
    permissao: 'OEE.OEE_DINAMICO',
    action: 'OEEDinamico',
  },
  {
    label: 'Paradas',
    icon: botaoParadas,
    permissao: 'OEE.PARADAS',
    action: 'Paradas',
  },
  {
    label: 'Consulta',
    icon: botaoConsulta,
    permissao: 'OEE.OEE_SEARCH',
    action: 'OEESearch',
  },
  {/*
    label: 'Auditoria',
    icon: botaoAuditoria,
    permissao: 'acessar_auditoria',
    action: 'TrilhaDeAuditoria',
  */},
  {
    label: 'OEE Setup',
    icon: botaoOeeSetup,
    permissao: 'OEE.OEE_SETUP',
    action: 'OEESetup',
  },
  {
    label: 'Paradas Setup',
    icon: botaoParadaSetup,
    permissao: 'OEE.PARADAS_SETUP',
    action: 'ParadasSetup',
  },
  {/*
    label: 'Voltar',
    icon: botaoVoltar,
    permissao: 'acessar_voltar', // ou nenhuma permissão, se for sempre visível
    action: 'Voltar',
  */},
];

const Layout = ({ children, onMenuClick}) => {
  const [currentTime, setCurrentTime] = useState('');
  const { usuario, carregando, atualizarUsuario } = useAuth();

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

  if (carregando) {
    return <div>Carregando autenticação...</div>; // Ou um Spinner
  }

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
            <p>Usuário: {usuario?.nome ? usuario.nome : 'não definido'}</p>
          </div>
          <div>
            <p>Hora: {currentTime}</p>
          </div>
        </div>
      </div>

      {/* Menu lateral */}
      <div className="sidebar">
        {MENU_ITEMS.map((item) => 
          usuario?.permissoes?.includes(item.permissao) ? (
            <div className='menu-item' key={item.label} onClick={() => onMenuClick(item.action)}>
              <img src={item.icon} alt={`Ícone ${item.label}`} />
              <p>{item.label}</p>
            </div>
          ) : null
        )}
      </div>

    </div>
  );
};

export default Layout;
