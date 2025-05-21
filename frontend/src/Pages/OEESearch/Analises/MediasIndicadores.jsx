// components/Medias.js

import React from 'react';
import GraficoCustomPieChart2 from '../../Graficos/GraficoCustomPieChart2';

// Funções para calcular as médias de OEE, Disponibilidade, Desempenho e Qualidade
const calcularMedia = (data, chave) => {
  return data.reduce((acc, item) => acc + item[chave], 0) / data.length;
};

const MediasIndicadores = ({ oeeData }) => {
  // Verificando se os dados estão carregados
  if (!oeeData || oeeData.length === 0) {
    return <p>Definir dados de busca...</p>;
  }

  // Calculando as médias
  const avgOEE = calcularMedia(oeeData, 'oee');
  const avgDisponibilidade = calcularMedia(oeeData, 'availability');
  const avgDesempenho = calcularMedia(oeeData, 'performance');
  const avgQualidade = calcularMedia(oeeData, 'quality');

  return (
    <div style={{ width: '100%', marginTop: '10px', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '10px', boxShadow: '0px 4px 6px rgba(0, 0, 0, 0.1)' }}>
      <h3 style={{ textAlign: 'center' }}>Médias do período</h3>
      <hr style={{ borderColor: '#aaa', width: '95%', marginBottom: '10px' }} />
      <label>Insights: Verificar a média geral no período.</label>

      {/* OEE */}
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginBottom: '30px' }}>
        <GraficoCustomPieChart2
          percentage={Number(avgOEE)}
          w={200}
          h={200}
          raioInterno={65}
          raioExterno={90}
        />
        <span style={{ marginTop: '10px', fontWeight: 'bold', color: '#333' }}>OEE</span>
      </div>

      {/* Disponibilidade, Desempenho, Qualidade */}
      <div style={{
        display: 'flex',
        flexWrap: 'wrap',
        justifyContent: 'center',
        gap: '30px',
        width: '100%'
      }}>
        {[ 
          { label: 'Disponibilidade', value: avgDisponibilidade },
          { label: 'Desempenho', value: avgDesempenho },
          { label: 'Qualidade', value: avgQualidade }
        ].map((item, idx) => (
          <div key={idx} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <GraficoCustomPieChart2
              percentage={Number(item.value)}
              w={150}
              h={150}
              raioInterno={50}
              raioExterno={70}
            />
            <span style={{ marginTop: '8px', fontWeight: 'bold', color: '#333' }}>{item.label}</span>
          </div>
        ))}
      </div>                
    </div>
  );
};

export default MediasIndicadores;
