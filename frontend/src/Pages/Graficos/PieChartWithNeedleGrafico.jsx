import React from 'react';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Customized,
} from 'recharts';
import './PieChartWithNeedleGrafico.css';

const RADIAN = Math.PI / 180;

const renderNeedle = (props) => {
  const { cx, cy, innerRadius, outerRadius, valor_real, valor_previsto } = props;
  const value = valor_real;
  const ang = 180.0 * (1 - value / valor_previsto);
  const length = (innerRadius + 2 * outerRadius) / 3;
  const sin = Math.sin(-RADIAN * ang);
  const cos = Math.cos(-RADIAN * ang);
  const r = 5;

  const x0 = cx;
  const y0 = cy;
  const xba = x0 + r * sin;
  const yba = y0 - r * cos;
  const xbb = x0 - r * sin;
  const ybb = y0 + r * cos;
  const xp = x0 + length * cos;
  const yp = y0 + length * sin;

  return (
    <g>
      <circle cx={x0} cy={y0} r={r} fill="#d0d000" stroke="none" />
      <path d={`M${xba},${yba} L${xbb},${ybb} L${xp},${yp} Z`} fill="#d0d000" stroke="none" />
    </g>
  );
};

const PieChartWithNeedleGrafico = ({ valor_real, valor_previsto }) => {
  const data = [
    { name: 'Baixo', value: valor_previsto / 3, color: '#FF4C4C' },
    { name: 'Médio', value: valor_previsto / 3, color: '#FFBB28' },
    { name: 'Alto', value: valor_previsto / 3, color: '#4CAF50' },
  ];

  const iR = 70;
  const oR = 100;

  return (
    <div style={{ display: 'flex', flexDirection: 'row', width: '100%', height: 200, alignItems: 'center' }}>
      <ResponsiveContainer width="100%" height={150}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="100%"
            startAngle={180}
            endAngle={0}
            dataKey="value"
            innerRadius={iR}
            outerRadius={oR}
            stroke="none"
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>

          {/* Desenha a agulha usando Customized */}
          <Customized
            component={({ width, height }) =>
              renderNeedle({
                cx: width / 2,
                cy: height,
                innerRadius: iR,
                outerRadius: oR,
                valor_real,
                valor_previsto,
              })
            }
          />
        </PieChart>
      </ResponsiveContainer>

      {/* Labels abaixo do gráfico */}
      <div className="info-label">
        <div className="info-card">
          <div className="info-title">Meta</div>
          <div className="info-value valor-meta">
            {valor_previsto}<span className="info-unit"> ppm</span>
          </div>
        </div>
        <div className="info-card">
          <div className="info-title">Produção atual</div>
          <div className="info-value valor-real">
            {valor_real}<span className="info-unit"> ppm</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PieChartWithNeedleGrafico;
