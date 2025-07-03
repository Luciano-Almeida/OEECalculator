// src/components/OEEDinamico.jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Legend } from 'recharts';
import { format } from "date-fns";
import LineSpeed from '../Graficos/LineSpeed';
import GraficoTemporal from '../Graficos/GraficoTemporal';
import GraficoCustomPieChart from '../Graficos/GraficoCustomPieChart';
import PieChartWithNeedleGrafico from '../Graficos/PieChartWithNeedleGrafico';
import ProductionChart from '../Graficos/ProductionChart';
import GraficoCustomPieChart2 from '../Graficos/GraficoCustomPieChart2';
import { useAuditoria } from '../../hooks/useAuditoria';
import { useAuth } from '../../context/AuthContext';

// Cores para os gráficos
const COLORS = ["#229752", '#1f8a4c', '#0088FE', '#00C49F', '#FFBB28', '#FF8042'];


const OEEDinamico = () => {
  const [cameraId, setCameraId] = useState(Number(import.meta.env.VITE_CAMERA_DEFAULT) || 1); 
  const cameras = import.meta.env.VITE_CAMERAS ? import.meta.env.VITE_CAMERAS.split(',') : [];
  const [responseData, setResponseData] = useState(null);
  const { registrarAuditoria } = useAuditoria();
  const { atualizarUsuario } = useAuth();

  const registrarAberturaTela = async () => {
    await registrarAuditoria("TELA OEE DINÂMICO", "Pesquisa OEE", "Acesso Permitido");
  };


  // Fetching data from the backend
  const fetchData = async () => {
    try {
      // Data e hora atuais
      const now = new Date();

      // Definindo o 'inicio' como o dia atual às 08:00
      const inicio = new Date(now);
      inicio.setHours(7, 0, 0); // Define a hora para 08:00:00:000

      // Função para formatar no formato ISO mas sem o ajuste para UTC
      const formatDateToLocalISO = (date) => {
        const localDate = new Date(date.getTime() - date.getTimezoneOffset() * 60000); // Ajusta para o horário local
        return localDate.toISOString().slice(0, 19); // Remove os milissegundos e "Z" do fuso horário
      };

      // Formatação para o formato ISO 8601 (YYYY-MM-DDTHH:mm:ss)
      const inicioISO = formatDateToLocalISO(inicio);
      const fimISO = formatDateToLocalISO(now);

      console.log("Início:", inicioISO);
      console.log("Fim:", fimISO);

      // Fazendo a requisição usando o Axios
      const response = await axios.get(`http://localhost:8000/oee`, {
        params: {
          //inicio: inicioISO,  // Passando a data e hora no formato desejado
          //fim: fimISO,        // Passando a data e hora no formato desejado
          hora_atual: fimISO,
          camera_name_id: cameraId
        }
      });


      setResponseData(response.data);
      console.log(response.data);

      // Atualiza o usuário
      if (response.data.autentication){
        atualizarUsuario(response.data.autentication);
      }
      else{
        console.log("Nenhum usuário ativo.");
        return <div>Nenhum Usuário Ativo...</div>; // Ou um Spinner
      }

    } catch (error) {
      console.error("Erro ao buscar os dados da API", error);
    }
  };

  useEffect(() => {
    // Chama o fetchData imediatamente e a cada 60 segundos
    fetchData();  // Chama imediatamente na primeira renderização
    registrarAberturaTela();
    const intervalId = setInterval(fetchData, 60000);  // 60.000ms = 1 minuto

    return () => clearInterval(intervalId);  // Limpa o intervalo quando o componente for desmontado
  }, [cameraId]);  // O array vazio faz com que o efeito seja executado apenas uma vez após a montagem do componente
  

  
  if (!responseData) {
    return <div>Carregando...</div>;
  }


  // Converte "HH:MM:SS" para segundos
  const timeStringToSeconds = (timeString) => {
    const [hours, minutes, seconds] = timeString.split(':').map(Number);
    return hours * 3600 + minutes * 60 + seconds;
  };


  // Calcula peças por minuto real
  const velocidade_real = Math.round(responseData['H_Total_pecas_produzidas'] / (timeStringToSeconds(responseData['F_Tempo_operando(D-E)']) / 60))
  // Formatando o turno atual para exibir na tela
  const turnoInicio = format(new Date(responseData['shift_atual'][0]), 'HH:mm');
  const turnoFim = format(new Date(responseData['shift_atual'][1]), 'HH:mm');
  const turnoTexto = `${turnoInicio} à ${turnoFim}`;

  if (!responseData['autentication']){
    return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      height: '80vh',
      backgroundColor: '#f8d7da',
      color: '#721c24',
      fontWeight: 'bold',
      fontSize: '1.2rem',
      border: '1px solid #f5c6cb',
      borderRadius: '8px',
      padding: '20px',
      boxShadow: '0px 4px 6px rgba(0, 0, 0, 0.1)',
      textAlign: 'center'
    }}>
      Nenhum Usuário Ativo...
    </div>
  );
  }  

  return (
    <div style={{ display: 'flex', flexDirection: 'column' }}>
      <div style={{ display: 'flex', flexDirection: 'row', justifyContent: 'space-between'}}>
        <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between'}}>
          {/* Quantidade produzida */}
          <div style={{ width: '100%', marginTop: '10px', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '10px', boxShadow: '0px 4px 6px rgba(0, 0, 0, 0.1)' }}>
            <h3 style={{ textAlign: 'center' }}>Produção (unidades)</h3>
            <hr style={{ borderColor: '#aaa', width: '95%' }} />
            <GraficoCustomPieChart 
              produzidoTotal={responseData["H_Total_pecas_produzidas"]} 
              produzidoBons={responseData["H_Total_pecas_produzidas"] - responseData["L_Total_pecas_defeituosas"]} 
              planejado={responseData["J_Max_pecas_possiveis(IxF)"]} 
            />
          </div>
        
          {/* LineSpeed2 PieChartWithNeedle */}
          <div style={{ width: '100%', marginTop: '10px', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '10px', boxShadow: '0px 4px 6px rgba(0, 0, 0, 0.1)' }}>
            <h3 style={{ textAlign: 'center' }}>Velocidade (ppm)</h3>
            <hr style={{ borderColor: '#aaa', width: '95%' }} />
            {/*<GraficoCustomPieChart valor_real={velocidade_real} valor_previsto={responseData['I_Tempo_ideal_ciclo']} />*/}
            <PieChartWithNeedleGrafico valor_real={velocidade_real} valor_previsto={responseData['I_Tempo_ideal_ciclo']} />
          </div>
        </div>

        {/* Seção de Indicadores */}
        <div style={{ width: '58%', marginTop: '10px', padding: '15px' , backgroundColor: '#f8f9fa', borderRadius: '10px', boxShadow: '0px 4px 6px rgba(0, 0, 0, 0.1)' }}>
          <h2 style={{ textAlign: 'center' }}>Indicadores de Performance</h2>
          <hr style={{ borderColor: '#aaa', width: '100%' }} />

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            {/* Turno atual */}
            <div style={{ fontWeight: 'bold', color: '#333' }}>
              Turno atual: {turnoTexto}
            </div>

            {/* Seletor de câmera (só aparece se houver mais de uma) */}
            {cameras.length > 1 && (
              <div style={{ display: 'flex', alignItems: 'center' }}>
                <label htmlFor='cameraSelector' style={{ marginRight: '10px', fontWeight: 'bold' }}>Câmera:</label>
                <select
                  id='cameraSelector'
                  value={cameraId}
                  onChange={(e) => setCameraId(Number(e.target.value))}
                  style={{ padding: '5px', borderRadius: '5px' }}
                >
                  {cameras.map((camera, index) => (
                    <option key={index} value={index + 1}>
                      {camera}
                    </option>
                  ))}
                </select>
              </div>
            )}
          </div>

          {/* OEE */}
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginBottom: '30px' }}>
            <GraficoCustomPieChart2
              percentage={Number(responseData['oee(GxKxM)'])}
              w={200}
              h={200}
              raioInterno={65}
              raioExterno={90}
            />
            <span style={{ marginTop: '10px', fontWeight: 'bold', color: '#333' }}>OEE</span>
          </div>

          {/* Disponibilidade, Desempenho, Qualidade */}
          <div style={{
            display: 'flex',
            justifyContent: 'center',
            width: '100%'
          }}>
            {[
              { label: 'Disponibilidade', value: responseData['G_Relacao_disponibilidade(F/D)'] },
              { label: 'Desempenho', value: responseData['K_Relacao_desempenho(H/J)'] },
              { label: 'Qualidade', value: responseData['M_Relacao_qualidade((H-L)/H)'] }
            ].map((item, idx) => (
              <div key={idx} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <GraficoCustomPieChart2
                  percentage={Number(item.value)}
                  w={150}
                  h={150}
                  raioInterno={50}
                  raioExterno={70}
                />
                <span style={{ marginTop: '8px', fontWeight: 'bold', color: '#333' }}>{item.label}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Histórico de Produção */}
      <div style={{ width: '100%', marginTop: '10px', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '10px', boxShadow: '0px 4px 6px rgba(0, 0, 0, 0.1)' }}>
        <h3 style={{ textAlign: 'center' }}>Histórico de Produção</h3>
        <hr style={{ borderColor: '#aaa', width: '95%' }} />
        <GraficoTemporal 
          discretizado={responseData['discretizado']} 
          startTime={format(new Date(responseData['shift_atual'][0]), 'HH:mm')} 
          endTime={format(new Date(responseData['shift_atual'][1]), 'HH:mm')} 
          paradas={responseData['setup_paradas_planejadas']}
        />
      </div>

      
    </div>
  );
};

export default OEEDinamico;
