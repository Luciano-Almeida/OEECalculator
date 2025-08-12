// components/GraficoBarrasHorizontal.js

import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

// Funções para calcular as médias de OEE, Disponibilidade, Desempenho e Qualidade
const calcularTotal = (data, chave) => {
  return data.reduce((acc, item) => acc + item[chave], 0);
};

const CustomLabel = ({ x, y, width, height, value, total }) => {
  const percent = ((value / total) * 100).toFixed(1);
  return (
    <text x={x + width + 5} y={y + (height /2) + 10} fill="#000" fontSize={22}>
      {`${percent}%`}
    </text>
  );
};

const TotalProduzido = ({ oeeData }) => {
  // Verificar se há dados
  if (!oeeData || oeeData.length === 0) {
    return <p></p>;
  }

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
  

  return (
    <div className="grafico-exportavel" style={{ width: '100%', marginTop: '10px', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '10px', boxShadow: '0px 4px 6px rgba(0, 0, 0, 0.1)' }}>
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
          <Bar 
            dataKey="Bons" 
            fill="#4CAF50" 
            label={(props) => <CustomLabel {...props} total={total_ok + total_nok} />}
          />
          <Bar 
            dataKey="Ruins" 
            fill="#F44336" 
            label={(props) => <CustomLabel {...props} total={total_ok + total_nok} />}
          />
        </BarChart>
      </ResponsiveContainer>
      
    </div>
  );
};

export default TotalProduzido;
