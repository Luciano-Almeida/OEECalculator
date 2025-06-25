import React from 'react';
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

const GraficoCustomPieChart2 = ({ percentage, w, h, raioInterno, raioExterno }) => {
    percentage = parseFloat(percentage.toFixed(2)) // duas casas decimais
  
    const remainingPercentage = parseFloat((100 - percentage).toFixed(2));;
    const chartData = [
      { name: 'Valor', value:  percentage},
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
          isAnimationActive={true}
        >
          <Cell fill="#0088FE" />
          <Cell fill="#E0E0E0" />
        </Pie>
        <Tooltip />
        <text x="50%" y="50%" textAnchor="middle" dominantBaseline="middle" fontSize="20" fill="#000" fontWeight='bold'>
          {`${percentage}%`}
        </text>
      </PieChart>
    );
  };
  

  export default GraficoCustomPieChart2;