// src/components/OEEDinamico.jsx
import React, { useState, useEffect } from 'react';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Legend } from 'recharts';
import { format } from "date-fns";
import LineSpeed from '../Graficos/LineSpeed';
import GraficoTemporal from '../Graficos/GraficoTemporal';
import GraficoCustomPieChart from '../Graficos/GraficoCustomPieChart';
import PieChartWithNeedleGrafico from '../Graficos/PieChartWithNeedleGrafico';

// Cores para os gráficos
const COLORS = ["#229752", '#1f8a4c', '#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

// Dados de exemplo para as paradas planejadas
const paradasPlanejadasData = [
  { name: 'Almoço', value: 94 },  // Exemplo: 30 minutos
  { name: 'Manutenção Corretiva', value: 22 }
];

const CustomPieChart = ({ percentage, label, w, h, raioInterno, raioExterno }) => {
  const remainingPercentage = 100 - percentage;
  const chartData = [
    { name: 'Valor', value: percentage },
    { name: 'Restante', value: remainingPercentage }
  ];

  return (
    <PieChart width={w} height={h}>
      <Pie
        data={chartData}
        cx="50%"
        cy="50%"
        innerRadius={raioInterno}
        outerRadius={raioExterno}
        fill="#8884d8"
        dataKey="value"
      >
        <Cell fill={COLORS[2]} />
        <Cell fill="#E0E0E0" />
      </Pie>
      <Tooltip />
      <text x="50%" y="50%" textAnchor="middle" dominantBaseline="middle" fontSize="20" fill="#000" fontWeight='bold'>
        {`${percentage}%`}
      </text>
      <text x="50%" y="60%" textAnchor="middle" dominantBaseline="middle" fontSize="16" fill="#000" fontWeight='bold'>
        {label}
      </text>
    </PieChart>
  );
};

const OEESearch = () => {
  const [responseData, setResponseData] = useState(null);

  // Fetching data from the backend
  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('http://localhost:8000/oee/?inicio=2025-03-14T08:00:00&fim=2025-03-14T17:00:00&camera_name_id=1');
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

  const secondsToTimeString = (seconds) => {
    const h = Math.floor(seconds / 3600).toString().padStart(2, '0');
    const m = Math.floor((seconds % 3600) / 60).toString().padStart(2, '0');
    const s = (seconds % 60).toString().padStart(2, '0');
    return `${h}:${m}:${s}`;
  };

  const tempoData = [
    {
      name: 'Tempo Total',
      raw: responseData['B_Tempo_total_disponivel'],
      Tempo: timeStringToSeconds(responseData['B_Tempo_total_disponivel'])
    },
    {
      name: 'Parada Planejada',
      raw: responseData['C_Paradas_planejadas'],
      Tempo: timeStringToSeconds(responseData['C_Paradas_planejadas'])
    },
    {
      name: 'Parada Não Planejada',
      raw: responseData['E_Paradas_nao_planejadas'],
      Tempo: timeStringToSeconds(responseData['E_Paradas_nao_planejadas'])
    },
    {
      name: 'Tempo Operando',
      raw: responseData['F_Tempo_operando(D-E)'],
      Tempo: timeStringToSeconds(responseData['F_Tempo_operando(D-E)'])
    }
  ];

  // Calcula peças por minuto real
  const velocidade_real = Math.round(responseData['H_Total_pecas_produzidas'] / (timeStringToSeconds(responseData['F_Tempo_operando(D-E)']) / 60))

  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap' }}>
      {/* Seção de Dados da Pesquisa */}
      <div style={{ width: '30%', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '10px', boxShadow: '0px 4px 6px rgba(0, 0, 0, 0.1)' }}>
        <h2 style={{ textAlign: 'center' }}>Dados da Pesquisa</h2>
        <hr style={{ borderColor: '#aaa', width: '95%' }} />
        <div style={{ display: 'flex', flexDirection: 'column', fontSize: '18px', fontWeight: 'bold' }}>
          <div style={{ color: '#333' }}>
            <p>Data de Inicio:</p>
            <p>{format(new Date(responseData['A_Inicio']), 'dd-MM-yyyy HH:mm:ss')}</p>
            <p>Data Fim:</p>
            <p>{format(new Date(responseData['A_Fim']), 'dd-MM-yyyy HH:mm:ss')}</p>
            <p>Tempo Total:</p>
            <p>{responseData['B_Tempo_total_disponivel']}</p>
          </div>  
        </div>
      </div>

      {/* Seção de Indicadores */}
      <div style={{ width: '70%', padding: '15px', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <h2>Indicadores de Performance</h2>
        <hr style={{ borderColor: '#aaa', width: '95%' }} />
        <div style={{ display: 'flex', width: '100%', justifyContent: 'center' }}>
          <div>
            <CustomPieChart percentage={Number(responseData['oee(GxKxM)'])} label="OEE" w={300} h={300} raioInterno={95} raioExterno={120} />
          </div>
          <div>
            <CustomPieChart percentage={Number(responseData['G_Relacao_disponibilidade(F/D)'])} label="Disponibilidade" w={200} h={200} raioInterno={65} raioExterno={90} />
          </div>
          <div>
            <CustomPieChart percentage={Number(responseData['K_Relacao_desempenho(H/J)'])} label="Desempenho" w={200} h={200} raioInterno={65} raioExterno={90} />
          </div>
          <div>
            <CustomPieChart percentage={Number(responseData['M_Relacao_qualidade(H-(L/H))'])} label="Qualidade" w={200} h={200} raioInterno={65} raioExterno={90} />
          </div>
        </div>
      </div>

      {/* Histórico de Produção */}
      <div style={{ width: '100%', marginTop: '10px', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '10px', boxShadow: '0px 4px 6px rgba(0, 0, 0, 0.1)' }}>
        <h3 style={{ textAlign: 'center' }}>Histórico de Produção</h3>
        <hr style={{ borderColor: '#aaa', width: '95%' }} />
        <GraficoTemporal discretizado={responseData['discretizado']} />
      </div>

      {/* LineSpeed RadialBarChart */}
      <div style={{ width: '40%', marginTop: '10px', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '10px', boxShadow: '0px 4px 6px rgba(0, 0, 0, 0.1)' }}>
        <h3 style={{ textAlign: 'center' }}>Capacidade de Produção Pç / min</h3>
        <hr style={{ borderColor: '#aaa', width: '95%' }} />
        <LineSpeed 
          velocidade_prevista={responseData['I_Tempo_ideal_ciclo']}
          velocidade_real={velocidade_real}
        />
      </div>

      {/* LineSpeed2 CustomBarChart */}
      <div style={{ width: '100%', maxWidth: '500px', marginTop: '10px', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '10px', boxShadow: '0px 4px 6px rgba(0, 0, 0, 0.1)' }}>
        <h3 style={{ textAlign: 'center' }}>Capacidade de Produção (ppm)</h3>
        <hr style={{ borderColor: '#aaa', width: '95%' }} />
        {/*<GraficoCustomPieChart valor_real={velocidade_real} valor_previsto={responseData['I_Tempo_ideal_ciclo']} />*/}
        <PieChartWithNeedleGrafico valor_real={velocidade_real} valor_previsto={responseData['I_Tempo_ideal_ciclo']} />
      </div>

      {/* Seção de Tempo de Produção (Gráfico de Barras) */}
      <div style={{ width: '60%', marginTop: '10px', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '10px', boxShadow: '0px 4px 6px rgba(0, 0, 0, 0.1)' }}>
        <h3 style={{ textAlign: 'center' }}>Tempos discretizados</h3>
        <hr style={{ borderColor: '#aaa', width: '95%' }} />
        <ResponsiveContainer width="100%" height={300}>
          <BarChart 
            data={tempoData}
            margin={{ top: 0, right: 0, left: 10, bottom: 0 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis tickFormatter={secondsToTimeString} />
            <Tooltip formatter={(Tempo) => secondsToTimeString(Tempo)} />
            <Bar dataKey="Tempo" fill={COLORS[2]} />

            
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Seção de Descrição das Paradas Planejadas */}
      <div style={{ width: '49%', marginTop: '10px', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '10px', boxShadow: '0px 4px 6px rgba(0, 0, 0, 0.1)' }}>
        <h3 style={{ textAlign: 'center' }}>Descrição das Paradas</h3>
        <hr style={{ borderColor: '#aaa', width: '95%' }} />
        <ResponsiveContainer width="100%" height={300}>
          <BarChart 
            width={600} 
            height={300} 
            data={paradasPlanejadasData} 
            layout="vertical"
            margin={{ top: 0, right: 0, left: 100, bottom: 0 }}
          >
            <XAxis type="number"/>
            <YAxis type="category" dataKey="name" />
            <CartesianGrid strokeDasharray="3 3"/>
            <Tooltip />
            <Legend />
            <Bar dataKey="value" fill={COLORS[2]} />
          </BarChart>
        </ResponsiveContainer>
      </div>


      

      

    </div>
  );
};

export default OEESearch;
