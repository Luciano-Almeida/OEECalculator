// components/GraficoLinha.js

import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import moment from 'moment';

const GraficoLinha = ({ oeeData }) => {
  // Verificar se há dados para exibir
  if (!oeeData || oeeData.length === 0) {
    return <p>Carregando dados...</p>;
  }

  // Preparando os dados para o gráfico
  const chartData = oeeData.map((item) => ({
    date: moment(item.init).format('DD/MM/YYYY HH:MM'), // Formatar a data
    OEE: item.oee,
    Disponibilidade: item.availability,
    Desempenho: item.performance,
    Qualidade: item.quality,
  }));

  console.log("linha", oeeData);

  return (
    <div style={{ width: '100%', marginTop: '10px', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '10px', boxShadow: '0px 4px 6px rgba(0, 0, 0, 0.1)' }}>
      <h3 style={{ textAlign: 'center' }}>Evolução do OEE, Disponibilidade, Desempenho e Qualidade</h3>
      <hr style={{ borderColor: '#aaa', width: '95%', marginBottom: '10px' }} />
      <label>Insights: Identificar padrões sazonais ou falhas repetitivas no período.</label>

      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="OEE" stroke="#8884d8" activeDot={{ r: 8 }} />
          <Line type="monotone" dataKey="Disponibilidade" stroke="#82ca9d" />
          <Line type="monotone" dataKey="Desempenho" stroke="#ff7300" />
          <Line type="monotone" dataKey="Qualidade" stroke="#00c49f" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default GraficoLinha;
