// src/Pages/OEEDinamico/DigestStatusProgressBar.jsx
import React from 'react';

const DigestStatusProgressBar = ({ statusDigest, digestTotal }) => {
  if (!statusDigest || statusDigest.status === "ok") return null;

  const { digest_time_control } = statusDigest;
  //const digestTotal = 500000; //digest_time_control;
  const totalTime = digestTotal || 500000;
  const remainingTime = Math.max(0, statusDigest.digest_time_control); 
  const percentage = Math.round((remainingTime / totalTime) * 100);

  // Definindo cores com base no status
  const barColor = statusDigest.status === "atrasado" ? "#dc3545" : "#ffc107"; // vermelho ou amarelo
  const textColor = statusDigest.status === "atrasado" ? "#721c24" : "#856404";

  return (
    <div style={{
      padding: '20px',
      backgroundColor: barColor + "22",
      border: `1px solid ${barColor}`,
      borderRadius: '10px',
      marginTop: '20px',
      textAlign: 'center',
      color: textColor,
      fontWeight: 'bold'
    }}>
      <p>Status: {statusDigest.status.toUpperCase()}</p>
      {/*<p>Tempo restante: {Math.round(remainingTime)} segundos</p>*/}
      <p>Faltando: {percentage}%</p>

      <div style={{
        width: '100%',
        height: '25px',
        backgroundColor: '#e9ecef',
        borderRadius: '8px',
        overflow: 'hidden',
        marginTop: '10px'
      }}>
        <div style={{
          width: `${percentage}%`,
          height: '100%',
          backgroundColor: barColor,
          transition: 'width 1s linear'
        }}></div>
      </div>
    </div>
  );
};

export default DigestStatusProgressBar;
