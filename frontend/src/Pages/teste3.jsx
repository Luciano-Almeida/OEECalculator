import React, { useState } from "react";
import axios from "axios";

const ParadasSearch = () => {
  const [cameraId, setCameraId] = useState("");
  const [inicio, setInicio] = useState("");
  const [fim, setFim] = useState("");
  const [paradas, setParadas] = useState([]);

  const buscarParadas = async () => {
    const response = await axios.get("http://localhost:8000/paradas_com_tipos/", {
      params: {
        camera_name_id: cameraId,
        inicio,
        fim,
      },
    });
    setParadas(response.data);
    console.log("resposta", response.data);
  };

  return (
    <div>
      <h2>Buscar Paradas</h2>
      <input
        type="number"
        placeholder="Camera ID"
        value={cameraId}
        onChange={(e) => setCameraId(e.target.value)}
      />
      <input
        type="datetime-local"
        value={inicio}
        onChange={(e) => setInicio(e.target.value)}
      />
      <input
        type="datetime-local"
        value={fim}
        onChange={(e) => setFim(e.target.value)}
      />
      <button onClick={buscarParadas}>Buscar</button>

      <ul style={{ backgroundColor: '#f0f0f0', padding: '10px' }}>
        {paradas.map((p) => (
          <li 
          key={p.paradaID}
          style={{
            backgroundColor: '#ffffff',
            margin: '10px 0',
            padding: '10px',
            borderRadius: '5px',
            color: '#333',
          }}
          >
            <strong>{p.paradaType.toUpperCase()}</strong> - {p.startTime} até {p.endTime} <br />
            <em>{p.paradaName}</em> | Obs: {p.obs}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default ParadasSearch;




