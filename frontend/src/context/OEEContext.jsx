import React, { createContext, useContext, useState } from 'react';

// Criação do contexto
const OEEContext = createContext();

// Criação do provider para envolver o seu componente
export const OEEProvider = ({ children }) => {
  const [responseData, setResponseData] = useState(null);

  return (
    <OEEContext.Provider value={{ responseData, setResponseData }}>
      {children}
    </OEEContext.Provider>
  );
};

// Hook para acessar o contexto
export const useOEE = () => useContext(OEEContext);
