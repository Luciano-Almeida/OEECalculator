import React from 'react';
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

const GraficoCustomPieChart = ({ produzido, planejado }) => {
  const clampedValorReal = Math.min(produzido, planejado);

  const data = [
    { name: 'Realizado', value: clampedValorReal },
    { name: 'Restante', value: planejado - clampedValorReal },
  ];

  const COLORS = ['#0088FE', '#eee'];

  return (
    <div style={{ display: 'flex', flexDirection: 'row', width: '100%', height: 200, alignItems: 'center' }}>
      <div style={{ width: '100%', height: 200 }}>
        <ResponsiveContainer>
          <PieChart>
            <Pie
              data={data}
              innerRadius={60}
              outerRadius={80}
              dataKey="value"
              isAnimationActive={true}
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* Labels abaixo do gráfico */}
      <div className="info-label">
        <div className="info-card">
          <div className="info-title">Meta</div>
          <div className="info-value valor-meta">
          {planejado} <span className="info-unit">unidades</span>
        </div>
        </div>
        <div className="info-card">
          <div className="info-title">Produzido</div>
          <div className="info-value valor-real">
          {produzido} <span className="info-unit">unidades</span>
          </div>
        </div>
      </div>

    </div>
  );
};

export default GraficoCustomPieChart;
