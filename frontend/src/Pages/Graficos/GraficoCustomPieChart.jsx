import React from 'react';
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

import './GraficoCustomPieChart.css';

const GraficoCustomPieChart = ({ produzidoTotal, produzidoBons, planejado }) => {
  const clampedValorReal = Math.min(produzidoTotal, planejado);
  const produzidoRuins = Math.max(produzidoTotal - produzidoBons, 0);

  // Dados do anel externo (meta vs produzido)
  const dataExterno2 = [
    { name: 'Produzido', value: clampedValorReal },
    { name: 'Restante', value: Math.max(planejado - clampedValorReal, 0) },
  ];
  const dataExterno = [
    { name: 'Bons', value: produzidoBons },
    { name: 'Ruins', value: produzidoRuins },
    { name: 'Restante', value: Math.max(planejado - clampedValorReal, 0) },
  ];

  // Dados do anel interno (bons vs ruins)
  const dataInterno = [
    { name: 'Bons', value: produzidoBons },
    { name: 'Ruins', value: produzidoRuins },
  ];

  const COLORS_EXTERNO = ['#0088FE', '#FF8042', '#ccc'];
  const COLORS_INTERNO = ['#00C49F', '#FF8042'];

  return (
    <div style={{ display: 'flex', flexDirection: 'row', width: '100%', maxHeight: '200px', minHeight: '100px', alignItems: 'center' }}>
      <div style={{ width: '100%' }}>
        <ResponsiveContainer width="100%" aspect={1}>
          <PieChart>
            {/* Anel externo - Total produzido vs Meta */}
            <Pie
              data={dataExterno}
              dataKey="value"
              outerRadius={80}
              innerRadius={60}
              isAnimationActive={true}
            >
              {dataExterno.map((entry, index) => (
                <Cell key={`cell-externo-${index}`} fill={COLORS_EXTERNO[index % COLORS_EXTERNO.length]} />
              ))}
            </Pie>

            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* Labels */}
      <div className="info-label-2">
        <div className="info-card-2">
          <div className="info-title-2">Meta</div>
          <div className="info-value-2 valor-meta-2">
            {Math.ceil(planejado)} <span className="info-unit-2">unidades</span>
          </div>
        </div>
        <div className="info-row-2">
          <div className="info-card-2">
            <div className="info-title-2">Bons </div>
            <div className="info-value-2 valor-real-2">
              {produzidoBons} 
            </div>
          </div>
          <div className="info-card-2">
            <div className="info-title-2">Ruins</div>
            <div className="info-value-2 valor-ruins-2" style={{color: COLORS_EXTERNO[1]}}>
              {produzidoRuins} 
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GraficoCustomPieChart;
