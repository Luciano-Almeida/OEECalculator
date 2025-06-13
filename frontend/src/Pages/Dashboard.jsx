// src/components/Dashboard.jsx
import React from 'react';
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as BarTooltip, Legend as BarLegend } from 'recharts';
import { useOEE } from '../context/OEEContext.jsx';

// Cores para os gráficos
const COLORS = ["#229752", '#1f8a4c', '#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

// Dados de exemplo para as paradas planejadas
const paradasPlanejadasData = [
  { name: 'Almoço', value: 30 },  // Exemplo: 30 minutos
  { name: 'Alongamento', value: 10 },
  { name: 'Manutenção', value: 20 },
  { name: 'Troca de Turno', value: 15 },
];

const CustomPieChart = ({ percentage, label, w, h, raioInterno, raioExterno }) => {
  const remainingPercentage = 100 - percentage;
  console.log(remainingPercentage)

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

const Dashboard = () => {
  const { responseData } = useOEE(); // Acesso aos dados do contexto
  // Definindo as datas de produção (exemplo de datas fixas)
  const dataDeProducao = {
    total: '10:00:00',
    lote: 'Lote 12345',
    observacoes: 'Sem observações importantes.',
    dataInicio: new Date('2025-01-01T08:00:00'),
    dataFim: new Date('2025-03-31T18:00:00')
  };

  const tempoData = [
    { name: 'Tempo Total', value: responseData['B_Tempo_total_disponivel'] },
    { name: 'Paradas Planejadas', value: responseData['C_Paradas_planejadas'] },
    { name: 'Paradas Não Planejadas', value: responseData['E_Paradas_nao_planejadas'] },
    { name: 'Tempo Operando', value: responseData['F_Tempo_operando(D-E)'] },
  ];

  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'flex-start', flexWrap: 'wrap' }}>
      {/* Seção de Dados da Pesquisa */}
      <div style={{ width: '30%', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '10px', boxShadow: '0px 4px 6px rgba(0, 0, 0, 0.1)' }}>
        <h2 style={{ textAlign: 'center' }}>Dados da Pesquisa</h2>
        <hr style={{ borderColor: '#aaa', width: '95%' }} />
        <div style={{ display: 'flex', flexDirection: 'column', fontSize: '18px', fontWeight: 'bold' }}>
          <div style={{ color: '#333' }}>
            <p>Data de Inicio:</p>
            <p>{responseData['A_inicio']}</p>
            <p>Data Fim:</p>
            <p>{responseData['A_fim']}</p>
            <p>Tempo Total:</p>
            <p>{responseData['B_Tempo_total_disponivel']} (min)</p>
          </div>  
        </div>
      </div>
      
      {/* Seção de Indicadores */}
      <div style={{ width: '70%', padding: '15px', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <h2>Indicadores de Performance</h2>
        <hr style={{ borderColor: '#aaa', width: '95%' }} />
        <div style={{ display: 'flex', width: '100%', justifyContent: 'center' }}>
          <div>
            <CustomPieChart percentage={Number(responseData['OEE'])} label="OEE" w={300} h={300} raioInterno={95} raioExterno={120} />
          </div>
          <div>
            <CustomPieChart percentage={Number(responseData['G_Relacao_disponibilidade(F/D)'])} label="Disponibilidade" w={200} h={200} raioInterno={65} raioExterno={90} />
          </div>
          <div>
            <CustomPieChart percentage={Number(responseData['K_Relacao_desempenho(H/J)'])} label="Desempenho" w={200} h={200} raioInterno={65} raioExterno={90} />
          </div>
          <div>
            <CustomPieChart percentage={Number(responseData['M_Relacao_qualidade(H-L/H)'])} label="Qualidade" w={200} h={200} raioInterno={65} raioExterno={90} />
          </div>
        </div>
      </div>
      
      {/* Seção de Tempo de Produção (Gráfico de Barras) */}
      <div style={{ width: '60%', marginTop: '10px', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '10px', boxShadow: '0px 4px 6px rgba(0, 0, 0, 0.1)' }}>
        <h3 style={{ textAlign: 'center' }}>Tempo de Produção</h3>
        <hr style={{ borderColor: '#aaa', width: '95%' }} />
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={tempoData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Bar dataKey="value" fill={COLORS[2]} />
            <BarTooltip />
            <BarLegend />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Seção de Dados de Produção */}
      <div style={{ width: '40%'}}>
      <div style={{ width: '100%', marginTop: '10px', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '10px', boxShadow: '0px 4px 6px rgba(0, 0, 0, 0.1)' }}>
        <h3 style={{ textAlign: 'center' }}>Dados de Produção</h3>
        <hr style={{ borderColor: '#aaa', width: '95%' }} />
        <div style={{ display: 'flex', flexDirection: 'column', fontSize: '18px', fontWeight: 'bold' }}>
          <div style={{ color: '#333' }}>
            <p>Total Produzido</p>
            <p>{responseData['H_Total_pecas_produzidas']}</p>
          </div>
          <div style={{ color: '#229752' }}>
            <p>Peças Boas</p>
            <p>{Number(responseData['H_Total_pecas_produzidas']) - Number(responseData['L_Total_pecas_ruins'])}</p>
          </div>
          <div style={{ color: '#FF8042' }}>
            <p>Peças Ruins</p>
            <p>{responseData['L_Total_pecas_ruins']}</p>
          </div>
        </div>
      </div>

      {/* Seção de Produção Ideal e Peças por Minuto */}
      <div style={{ width: '100%', marginTop: '30px', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '10px', boxShadow: '0px 4px 6px rgba(0, 0, 0, 0.1)' }}>
        <h3 style={{ textAlign: 'center' }}>Produção Ideal e Peças por Minuto</h3>
        <hr style={{ borderColor: '#aaa', width: '95%' }} />
        <div style={{ display: 'flex', justifyContent: 'space-around', fontSize: '18px', fontWeight: 'bold' }}>
          <div style={{ color: '#229752' }}>
            <p>Peças por Minuto</p>
            <p>{responseData['I_Tempo_ideal_ciclo']} (pç / min)</p> {/* Exemplo de valor */}
          </div>
          <div style={{ color: '#FF8042' }}>
            <p>Produção Ideal</p>
            <p>{responseData['J_Numero_maximo_pecas_que_podem_ser_produzidas(IxF)']}</p> {/* Exemplo de valor */}
          </div>
        </div>
      </div>
      </div>
      {/* Descrição das Paradas Planejadas */}
      <div style={{ width: '60%', marginTop: '30px', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '10px', boxShadow: '0px 4px 6px rgba(0, 0, 0, 0.1)' }}>
        <h3 style={{ textAlign: 'center' }}>Descrição das Paradas Planejadas</h3>
        <hr style={{ borderColor: '#aaa', width: '95%' }} />
        <ResponsiveContainer width="100%" height={300}>
        <BarChart 
          width={600} 
          height={300} 
          data={paradasPlanejadasData} 
          layout="vertical"
          margin={{top: 5, right: 30, left: 50, bottom: 5}}
        >
          <XAxis type="number"/>
          <YAxis type="category" dataKey="name" />
          <CartesianGrid strokeDasharray="3 3"/>
          <Tooltip/>
          <Legend />
          <Bar dataKey="value" fill={COLORS[2]} />
        </BarChart>
        </ResponsiveContainer>
      </div>

    </div>
  );
};

export default Dashboard;

