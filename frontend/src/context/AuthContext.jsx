import React, { createContext, useContext, useEffect, useState } from "react";
import axios from "axios";

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [usuario, setUsuario] = useState(null);
    const [carregando, setCarregando] = useState(true);

    useEffect(() => {
        const autenticar = async () => {
            try {
                const response = await axios.get('http://localhost:8000/autentication');
                setUsuario(response.data); // Ex: { nome, permissoes }
            } catch (error) {
                console.error('Erro na autenticação:', error);
                setUsuario(null);
            } finally {
                setCarregando(false);
            }
        };

        autenticar();
    }, []);

    return (
        <AuthContext.Provider value={{ usuario, carregando}}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);