import React from 'react';
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

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
    <div style={{ display: 'flex', flexDirection: 'row', width: '100%', height: 200, alignItems: 'center' }}>
      <div style={{ width: '100%', height: 200 }}>
        <ResponsiveContainer>
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

            {/* Anel interno - Bons vs Ruins 
            <Pie
              data={dataInterno}
              dataKey="value"
              outerRadius={55}
              innerRadius={40}
              isAnimationActive={true}
            >
              {dataInterno.map((entry, index) => (
                <Cell key={`cell-interno-${index}`} fill={COLORS_INTERNO[index % COLORS_INTERNO.length]} />
              ))}
            </Pie>*/}

            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* Labels */}
      <div className="info-label">
        <div className="info-card">
          <div className="info-title">Meta</div>
          <div className="info-value valor-meta">
            {Math.ceil(planejado)} <span className="info-unit">unidades</span>
          </div>
        </div>
        <div style={{display: "flex", gap: "20px"}}>
          <div className="info-card">
            <div className="info-title">Bons </div>
            <div className="info-value valor-real">
              {produzidoBons} 
            </div>
          </div>
          <div className="info-card">
            <div className="info-title">Ruins</div>
            <div className="info-value valor-ruins" style={{color: COLORS_EXTERNO[1]}}>
              {produzidoRuins} 
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GraficoCustomPieChart;
