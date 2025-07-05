import { useState, useEffect } from 'react';

import axios from "axios";

import './App.css';
import { AuthProvider, useAuth} from './context/AuthContext'
import MainContent from './Components/MainContent';
import StatusSetup from './Pages/Status/StatusSetup';

function App() {
  const [currentPage, setCurrentPage] = useState('OEEDinamico');
  const [isOeeReady, setIsOeeReady] = useState(null); // Estado para verificar o status de setup
  const [camerasFaltandoSetup, setcamerasFaltandoSetup] = useState([]);
  const [isLoading, setIsLoading] = useState(true); // Estado para controlar o carregamento do status inicial

  const checkSetupStatus = async () => {
    try {
      const response = await axios.get('http://localhost:8000/get_setup_status_ok');
      if (response.data.oee_ready) {
        setIsOeeReady(true);
      } else {
        setIsOeeReady(false);
        setcamerasFaltandoSetup(response.data.cameras_faltando_setup);
        console.log('cameras_faltando_setup', response.data.cameras_faltando_setup);
      }
      console.log('Status do OEE', response.data.oee_ready, 'câmeras faltando', response.data.cameras_faltando_setup);
    } catch (error) {
      console.error('Erro ao verificar status de setup:', error);
      setIsOeeReady(false);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    checkSetupStatus();
  }, []);


  const reviewStatus = async () => {
    setIsLoading(true);
    await checkSetupStatus(); // Re-chama a função que verifica o status
  };
  
  if (isLoading) {
    return <div>
      Carregando configuração inicial...
    </div>; // Exibir carregando enquanto aguarda a resposta
  }

  return (
    <AuthProvider>
      <MainContent
        currentPage={currentPage}
        setCurrentPage={setCurrentPage}
        isOeeReady={isOeeReady}
        reviewStatus={reviewStatus}
        camerasFaltandoSetup={camerasFaltandoSetup}
      />
    </AuthProvider>
  );
}

export default App;








