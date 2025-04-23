import React, { useState } from "react";
import {
  PieChart,
  Pie,
  Sector,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import "./CustomActiveShapePieChart.css";

// Custom shape para destacar a fatia ativa
const renderActiveShape = (props) => {
  const RADIAN = Math.PI / 180;
  const { cx, cy, midAngle, innerRadius, outerRadius, startAngle, endAngle, fill, payload, percent, value } = props;
  const sin = Math.sin(-RADIAN * midAngle);
  const cos = Math.cos(-RADIAN * midAngle);
  const sx = cx + (outerRadius + 10) * cos;
  const sy = cy + (outerRadius + 10) * sin;
  const mx = cx + (outerRadius + 30) * cos;
  const my = cy + (outerRadius + 30) * sin;
  const ex = mx + (cos >= 0 ? 1 : -1) * 22;
  const ey = my;
  const textAnchor = cos >= 0 ? 'start' : 'end';

  return (
    <g>
      <text x={cx} y={cy} dy={8} textAnchor="middle" fill={fill}>
        {payload.name}
      </text>
      <Sector
        cx={cx}
        cy={cy}
        innerRadius={innerRadius}
        outerRadius={outerRadius}
        startAngle={startAngle}
        endAngle={endAngle}
        fill={fill}
      />
      <Sector
        cx={cx}
        cy={cy}
        startAngle={startAngle}
        endAngle={endAngle}
        innerRadius={outerRadius + 6}
        outerRadius={outerRadius + 10}
        fill={fill}
      />
      <path d={`M${sx},${sy}L${mx},${my}L${ex},${ey}`} stroke={fill} fill="none" />
      <circle cx={ex} cy={ey} r={2} fill={fill} stroke="none" />
      <text x={ex + (cos >= 0 ? 1 : -1) * 12} y={ey} textAnchor={textAnchor} fill="#333">{`PV ${value}`}</text>
      <text x={ex + (cos >= 0 ? 1 : -1) * 12} y={ey} dy={18} textAnchor={textAnchor} fill="#999">
        {`(Rate ${(percent * 100).toFixed(2)}%)`}
      </text>
    </g>
  );
};

const CustomActiveShapePieChart = ({ produzido, planejado }) => {
  const [activeIndex, setActiveIndex] = useState(0);

  const data = [
    { name: "Produzido", value: produzido },
    { name: "Planejado", value: planejado }
  ];

  const COLORS = ["#4caf50", "#f44336"];

  const onPieEnter = (_, index) => {
    setActiveIndex(index);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', textAlign: 'center', width: '100%', maxWidth: '500px', margin: '10px auto' }}>
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            activeIndex={activeIndex}
            activeShape={renderActiveShape}
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
            onMouseEnter={onPieEnter}
            nameKey="name"
            stroke="none"
          >
            {data.map((entry, index) => (
              <cell
                key={`cell-${index}`}
                fill={COLORS[index % COLORS.length]}
              />
            ))}
          </Pie>
          <Tooltip formatter={(value) => `${value} unidades`} />
        </PieChart>
      </ResponsiveContainer>
      
      {/* Labels abaixo do gráfico */}
      <div className="info-label">
        <div className="info-card">
          <div className="info-title">Produzido</div>
          <div className="info-value valor-real">
          {produzido} unidades
          </div>
        </div>
        <div className="info-card">
          <div className="info-title">Meta</div>
          <div className="info-value valor-meta">
          {planejado} unidades
          </div>
        </div>
      </div>
    </div>
  );
};

export default CustomActiveShapePieChart;
