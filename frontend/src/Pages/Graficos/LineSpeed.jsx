// src/components/LineSpeed.jsx
import React from 'react';
import {
  RadialBarChart,
  RadialBar,
  Legend,
  Tooltip,
  ResponsiveContainer
} from 'recharts';

const LineSpeed = ({ velocidade_prevista, velocidade_real }) => {
  const data = [
    {
      name: 'Capacidade Real',
      valor: velocidade_real,
      fill: '#82ca9d',
    },
    {
      name: 'Capacidade Prevista',
      valor: velocidade_prevista,
      fill: '#000',
    }
  ];

  return (
    <div style={{ textAlign: 'center' }}>
        
        <RadialBarChart
            width={300}
            height={300}
            cx="50%"
            cy="50%"
            innerRadius="50%"
            outerRadius="90%"
            barSize={25}
            data={data}
        >
            <RadialBar
            minAngle={15}
            label={{ position: 'insideStart', fill: '#fff' }}
            background
            clockWise
            dataKey="valor"
            />
            <Legend
            iconSize={10}
            width={120}
            height={140}
            layout="vertical"
            verticalAlign="middle"
            wrapperStyle={{ top: 0, left: 350, lineHeight: '24px' }}
            />
            <Tooltip />
        </RadialBarChart>
        
    </div>
  );
};

export default LineSpeed;
