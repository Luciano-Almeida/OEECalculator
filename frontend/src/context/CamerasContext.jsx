import React, { createContext, useState, useContext, useEffect} from "react";
import axios from 'axios';

// Contexto para as câmeras
const CamerasContext = createContext();

export const useCameras = () => {
    return useContext(CamerasContext);
};

export const CameraProvider = ({ children }) => {
    const [cameras, setCameras] = useState([]);
    const [cameraDefault, setCameraDefault] = useState(1);

    // Função para pegar as câmeras disponíveis
    const fetchCameras = async () => {
        try {
            const response = await axios.get('http://localhost:8000/get_cameras_disponiveis');
            setCameras(response.data.cameras_disponiveis);
            setCameraDefault(response.data.cameras_disponiveis[0] || 1); // Primeiro índice
        } catch (error) {
            console.error('Erro ao buscar as câmeras:', error);
        }
    };

    useEffect(() => {
        fetchCameras();
    }, []);

    return (
        <CamerasContext.Provider value={{ cameras, cameraDefault }}>
            {children}
        </CamerasContext.Provider>
    );
};