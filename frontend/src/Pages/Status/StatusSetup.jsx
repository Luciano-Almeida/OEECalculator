import React from 'react';

import './StatusSetup.css';

const StatusSetup = ({ onReviewStatus, camerasFaltandoSetup }) => {
  const isSingular = camerasFaltandoSetup.length === 1;
  const cameraText = camerasFaltandoSetup.join(', ');

  return (
    <div className="status-setup">
      <h2>Configuração Setup OEE Não Completa</h2>
      <p>O sistema não está pronto para operação. Por favor, configure o OEE Setup e as Paradas Setup 
        {isSingular ? ' da câmera ' : ' das câmeras '}{cameraText}.
      </p>
      <button onClick={onReviewStatus}>Configuração Completa</button>
    </div>
  );
};

export default StatusSetup;
