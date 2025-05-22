import React from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";


const DowntimeChart = ({ oeeData }) => {
  // Verificar se há dados para exibir
  if (!oeeData || oeeData.length === 0) {
    return <p></p>;
  }

  // Transformando os dados para o formato aceito pelo Recharts
  const chartData = oeeData.map((item) => ({
    name: new Date(item.init).toLocaleString("pt-BR", {
      day: "2-digit",
      month: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    }),
    planejadas: item.downtime_summary.planejadas,
    nao_planejadas: item.downtime_summary.nao_planejadas,
    nao_justificadas: item.downtime_summary.nao_justificadas,
  }));

  return (
    <ResponsiveContainer width="100%" height={400}>
      <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="name" />
        <YAxis label={{ value: 'Minutos', angle: -90, position: 'insideLeft' }} />
        <Tooltip />
        <Legend />
        <Bar dataKey="planejadas" fill="#8884d8" name="Planejadas" />
        <Bar dataKey="nao_planejadas" fill="#82ca9d" name="Não Planejadas" />
        <Bar dataKey="nao_justificadas" fill="#ff7300" name="Não Justificadas" />
      </BarChart>
    </ResponsiveContainer>
  );
};

export default DowntimeChart;
