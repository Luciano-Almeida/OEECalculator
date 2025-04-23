import React from "react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  LabelList
} from "recharts";
import "./ProductionChart.css";

const ProductionChart = ({ data }) => {
  return (
    <div className="chart-container">
      <h2>Comparativo de Produção</h2>
      <ResponsiveContainer width="100%" height={400}>
        <BarChart
          data={data}
          margin={{ top: 20, right: 30, left: 20, bottom: 50 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="nome" />
          <YAxis />
          <Tooltip />
          <Legend
            verticalAlign="bottom"
            height={50}
            wrapperStyle={{ paddingTop: "20px" }}
            formatter={(value) =>
              value === "produzido" ? "Quantidade Produzida" : "Quantidade Planejada"
            }
          />
          <Bar dataKey="produzido" fill="#4caf50" name="Quantidade Produzida">
            <LabelList dataKey="produzido" position="top" />
          </Bar>
          <Bar dataKey="planejado" fill="#f44336" name="Quantidade Planejada">
            <LabelList dataKey="planejado" position="top" />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default ProductionChart;
