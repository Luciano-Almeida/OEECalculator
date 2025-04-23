import React from 'react';
import './Relatorio.css'; // Você pode personalizar a estilização deste componente

const Relatorio = () => {
  // Exemplo de dados fictícios para o relatório
  const data = [
    { id: 1, nome: 'Máquina A', produção: 1000, tempo: '2h 30m', status: 'Ok' },
    { id: 2, nome: 'Máquina B', produção: 850, tempo: '3h 10m', status: 'Parada' },
    { id: 3, nome: 'Máquina C', produção: 950, tempo: '2h 50m', status: 'Ok' },
    { id: 4, nome: 'Máquina D', produção: 780, tempo: '3h 00m', status: 'Ok' },
  ];

  return (
    <div className="relatorio-container">
      <h2>Relatório de Produção</h2>
      
      {/* Tabela com os dados do relatório */}
      <table className="relatorio-tabela">
        <thead>
          <tr>
            <th>ID</th>
            <th>Máquina</th>
            <th>Produção</th>
            <th>Tempo de Produção</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {data.map((item) => (
            <tr key={item.id}>
              <td>{item.id}</td>
              <td>{item.nome}</td>
              <td>{item.produção}</td>
              <td>{item.tempo}</td>
              <td>{item.status}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Você pode adicionar mais informações, gráficos ou filtros aqui */}
    </div>
  );
};

export default Relatorio;
