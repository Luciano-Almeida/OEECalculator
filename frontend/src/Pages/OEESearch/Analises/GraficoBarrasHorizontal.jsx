// components/GraficoBarrasHorizontal.js

import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

// Funções para calcular as médias de OEE, Disponibilidade, Desempenho e Qualidade
const calcularTotal = (data, chave) => {
  return data.reduce((acc, item) => acc + item[chave], 0);
};

const GraficoBarrasHorizontal = ({ oeeData }) => {
  // Verificar se há dados
  if (!oeeData || oeeData.length === 0) {
    return <p>Carregando dados...</p>;
  }

  // Preparar os dados para o gráfico
  /*
  const chartData = oeeData.map((item, index) => ({
    turno: `Turno ${index + 1}`,
    total_ok: item.total_ok,
    total_nok: item.total_not_ok,
    total: item.total_ok + item.total_not_ok,
  }));
  */

  // Calculando as médias
  const total_ok = calcularTotal(oeeData, 'total_ok');
  const total_nok = calcularTotal(oeeData, 'total_not_ok');

  const chartData = [
    {
      turno: 'Produção',
      Bons: total_ok,
      Ruins: total_nok,
    },
  ];
  
  console.log("chat", chartData)


  return (
    <div style={{ width: '100%', marginTop: '10px', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '10px', boxShadow: '0px 4px 6px rgba(0, 0, 0, 0.1)' }}>
      <h3 style={{ textAlign: 'center' }}>Total de Produção: Bons vs Ruins</h3>
      <hr style={{ borderColor: '#aaa', width: '95%', marginBottom: '10px' }} />
      <label>Insights: Total de produção no período</label>

      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData} layout="vertical" margin={{ top: 20, right: 30, left: 80, bottom: 20 }}> 
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis type="number" />
          <YAxis dataKey="turno" type="category" />
          <Tooltip />
          <Legend />
          <Bar dataKey="Bons" fill="#4CAF50" />
          <Bar dataKey="Ruins" fill="#F44336" />
        </BarChart>
      </ResponsiveContainer>
      
    </div>
  );
};

export default GraficoBarrasHorizontal;
