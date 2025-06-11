import { useState } from 'react';

// Função que formata a data para "YYYY-MM-DD HH:MM:SS" no horário local
const getFormattedDateLocal = (date) => {
  const pad = (n) => String(n).padStart(2, '0');
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;
};

export const useDataInicioFim = () => {
  const now = new Date();

  // Precisamos criar duas instâncias separadas para evitar que `now` seja alterado
  const startOfDay = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 0, 0, 0, 0);
  const endOfDay = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 23, 59, 59, 999);

  const [inicio, setInicio] = useState(getFormattedDateLocal(startOfDay));
  const [fim, setFim] = useState(getFormattedDateLocal(endOfDay));

  return { inicio, setInicio, fim, setFim };
};
