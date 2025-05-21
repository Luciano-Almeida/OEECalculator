// src/components/OEEDinamico.jsx
import React, { useState, useEffect } from 'react';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Legend } from 'recharts';
import { format } from "date-fns";
import LineSpeed from '../Graficos/LineSpeed';
import GraficoTemporal from '../Graficos/GraficoTemporal';
import GraficoCustomPieChart from '../Graficos/GraficoCustomPieChart';
import PieChartWithNeedleGrafico from '../Graficos/PieChartWithNeedleGrafico';
import ProductionChart from '../Graficos/ProductionChart';
import CustomActiveShapePieChart from '../Graficos/CustomActiveShapePieChart';
import GraficoCustomPieChart2 from '../Graficos/GraficoCustomPieChart2';

// Cores para os gráficos
const COLORS = ["#229752", '#1f8a4c', '#0088FE', '#00C49F', '#FFBB28', '#FF8042'];


const OEEDinamico = () => {
  const [responseData, setResponseData] = useState(null);

  // Fetching data from the backend
  useEffect(() => {
    
    const fetchData = async () => {
      try {
        const response = await fetch('http://localhost:8000/oee/?inicio=2025-03-14T09:00:00&fim=2025-03-14T15:00:00&camera_name_id=1');
        if (response.ok) {
          const data = await response.json();
          setResponseData(data);
          console.log(data)
        } else {
          console.error("Erro ao buscar os dados da API");
        }
      } catch (error) {
        console.error("Erro ao conectar ao backend:", error);
      }
    };

    fetchData();
  }, []);  // O array vazio faz com que o efeito seja executado apenas uma vez após o componente ser montado

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

  const sampleData = [
    { nome: "", produzido: 120, planejado: 100 },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'stretch' }}>
      <div style={{ display: 'flex', flexDirection: 'row', justifyContent: 'space-between'}}>
        <div style={{ display: 'flex', width: '35%', marginLeft: '40px', flexDirection: 'column', justifyContent: 'space-between'}}>
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
        <div style={{ width: '58%', marginTop: '10px', marginRight: '40px', padding: '15px' , backgroundColor: '#f8f9fa', borderRadius: '10px', boxShadow: '0px 4px 6px rgba(0, 0, 0, 0.1)' }}>
          <h2 style={{ textAlign: 'center' }}>Indicadores de Performance</h2>
          <hr style={{ borderColor: '#aaa', width: '100%' }} />

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
            flexWrap: 'wrap',
            justifyContent: 'center',
            gap: '30px',
            width: '100%'
          }}>
            {[
              { label: 'Disponibilidade', value: responseData['G_Relacao_disponibilidade(F/D)'] },
              { label: 'Desempenho', value: responseData['K_Relacao_desempenho(H/J)'] },
              { label: 'Qualidade', value: responseData['M_Relacao_qualidade(H-(L/H))'] }
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
        <GraficoTemporal discretizado={responseData['discretizado']} />
      </div>

      
    </div>
  );
};

export default OEEDinamico;
