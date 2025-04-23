import React, { useState } from 'react';
import './TesteOEESetup.css';
import ShiftForm from './ShiftForm';
import ShiftList from './ShiftList';

const cameraOptions = ['Câmera IP', 'Webcam USB', 'Câmera Industrial', 'Câmera Virtual'];

const TesteOEESetup = () => {
  const [shifts, setShifts] = useState([]);
  const [shiftName, setShiftName] = useState('');
  const [startTime, setStartTime] = useState('');
  const [endTime, setEndTime] = useState('');
  const [selectedDays, setSelectedDays] = useState([]);
  const [editingId, setEditingId] = useState(null);

  const [cameraType, setCameraType] = useState('');
  const [cycleTime, setCycleTime] = useState('');
  const [machineStopTime, setMachineStopTime] = useState('');
  const [dataSummaryInterval, setDataSummaryInterval] = useState('');
  
  const handleDayToggle = (day) => {
    setSelectedDays((prev) =>
      prev.includes(day) ? prev.filter(d => d !== day) : [...prev, day]
    );
  };

  const handleFormChange = (field, value) => {
    if (field === 'shiftName') setShiftName(value);
    else if (field === 'startTime') setStartTime(value);
    else if (field === 'endTime') setEndTime(value);
  };

  const handleAddOrUpdateShift = () => {
    if (!shiftName || !startTime || !endTime || selectedDays.length === 0) return;

    const newShift = {
      name: shiftName,
      startTime,
      endTime,
      days: selectedDays,
      tempId: editingId || Date.now()
    };

    if (editingId) {
      setShifts(shifts.map(s => (s.tempId === editingId ? newShift : s)));
      setEditingId(null);
    } else {
      setShifts([...shifts, newShift]);
    }

    setShiftName('');
    setStartTime('');
    setEndTime('');
    setSelectedDays([]);
  };

  const handleEditShift = (shift) => {
    setShiftName(shift.name);
    setStartTime(shift.startTime);
    setEndTime(shift.endTime);
    setSelectedDays(shift.days);
    setEditingId(shift.tempId);
  };

  const handleDeleteShift = (shift) => {
    setShifts(shifts.filter(s => s.tempId !== shift.tempId));
  };

  const handleSubmit = () => {
    const config = {
      shifts,
      cameraType,
      cycleTime: Number(cycleTime),
      machineStopTime: Number(machineStopTime),
      dataSummaryInterval: Number(dataSummaryInterval)
    };
    console.log('Configuração do OEE:', config);
    alert('✅ Configuração salva com sucesso!');
  };

  return (
    <div className="oee-container">
      <h2>🛠️ Configuração do OEE</h2>

      {/* Câmera */}
      <section className="oee-section">
        <h3>📷 Tipo de Câmera</h3>
        <select value={cameraType} onChange={(e) => setCameraType(e.target.value)}>
          <option value="">Selecione...</option>
          {cameraOptions.map((type, index) => (
            <option key={index} value={type}>{type}</option>
          ))}
        </select>
      </section>

      {/* Turnos */}
      <section className="oee-section">
        <h3>🕒 Turnos de Produção</h3>
        <ShiftForm
          shiftName={shiftName}
          startTime={startTime}
          endTime={endTime}
          selectedDays={selectedDays}
          onChange={handleFormChange}
          onDayToggle={handleDayToggle}
          onSubmit={handleAddOrUpdateShift}
          isEditing={!!editingId}
        />
        <ShiftList shifts={shifts} onEdit={handleEditShift} onDelete={handleDeleteShift} />
      </section>

      {/* Parâmetros Técnicos */}
      <section className="oee-section">
        <h3>⚙️ Parâmetros Técnicos</h3>
        <div className="oee-inputs-grid">
          <div>
            <label>Tempo de Ciclo (PPM)</label>
            <input
              type="number"
              placeholder="Peças por minuto"
              value={cycleTime}
              onChange={(e) => setCycleTime(e.target.value)}
            />
          </div>
          <div>
            <label>Parada da Máquina (s)</label>
            <input
              type="number"
              placeholder="Segundos"
              value={machineStopTime}
              onChange={(e) => setMachineStopTime(e.target.value)}
            />
          </div>
          <div>
            <label>Resumo dos Dados (s)</label>
            <input
              type="number"
              placeholder="Segundos"
              value={dataSummaryInterval}
              onChange={(e) => setDataSummaryInterval(e.target.value)}
            />
          </div>
        </div>
      </section>

      <button className="btn primary" onClick={handleSubmit}>💾 Salvar Configuração</button>
    </div>
  );
};

export default TesteOEESetup;



/*
import React, { useState, useEffect } from 'react';
import './OEESetup.css';
import { format } from 'date-fns';
import { useOEE } from '../../Components/OEEContext';



const OEESetup = () => {
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [cycleTime, setCycleTime] = useState('120');
  const [stopedMachine, setStopedMachine] = useState('5');
  const [intervaloResumo, setIntervaloResumo] = useState(60); // Exemplo inicial de 600 segundos
  const [totalPlannedStops, setTotalPlannedStops] = useState('0');
  const [cameraTypes, setCameraTypes] = useState(['Camera01', 'Camera02', 'Camera03', 'Camera04', 'Camera05', 'Camera06', 'Camera07', 'Camera08', 'Camera09']);
  const [cameraType, setCameraType] = useState('Camera01');
  const { responseData, setResponseData } = useOEE(null); // Acesso ao contexto


  // Função para calcular a data de início e fim
  const setDates = () => {
    const now = new Date();

    // Setando a data de início com 8 horas a menos
    const start = new Date(now);
    start.setHours(now.getHours() - 8);
    setStartDate(start.toISOString().slice(0, 16)); // Formato para input "datetime-local"

    // Setando a data de término com a hora atual
    const end = new Date(now);
    setEndDate(end.toISOString().slice(0, 16)); // Formato para input "datetime-local"
  };

  // Usando o hook useEffect para definir as datas assim que o componente for montado
  useEffect(() => {
    setDates();
  }, []);


  // Função para enviar os dados para o backend FastAPI
  const handleSubmit = async () => {
    const formatoStartDate = format(startDate, 'yyyy-MM-dd HH:mm:ss');
    const formatoEndDate = format(endDate, 'yyyy-MM-dd HH:mm:ss');

    const data = {
      startDate: formatoStartDate,  // Formato ISO 8601
      endDate: formatoEndDate,      // Formato ISO 8601
      cycleTime,
      stopedMachine,
      totalPlannedStops,
      cameraType, // Enviando o tipo de câmera
      };

      console.log(data);

    try{
      const response = await fetch('http://localhost:8000/oee_search', {
        method: 'POST',
        headers: {  
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      if (response.ok){
        const result = await response.json();
        setResponseData(result); // Armazena a resposta recebida do backend
        console.log(result);
      } else {
        console.error('Erro ao enviar os dados:', response.statusText);
      }
    } catch(error){
      console.error('Erro ao enviar os dados:', error);
    }
  };

  return (
    <div className="search-bar">
      <div className="item_search">
        <h3>Data de Início da produção</h3>
        <input 
          type="datetime-local" 
          value={startDate} 
          onChange={(e) => setStartDate(e.target.value)} 
        />
      </div>
      <div className="item_search">
        <h3>Data de Término da produção</h3>
        <input 
          type="datetime-local" 
          value={endDate} 
          onChange={(e) => setEndDate(e.target.value)} 
        />
      </div>
      <div className="item_search">
        <h3>Tipo de Câmera</h3>
        <select
          value={cameraType}
          onChange={(e) => setCameraType(e.target.value)} // Atualiza o tipo de câmera
        >
          {cameraTypes.map((type, index) => (
            <option key={index} value={type}>
              {type}
            </option>
          ))}
        </select>
      </div>
      <div className="item_search">
        <h3>Tempo de ciclo (pç / min)</h3>
        <input 
          type="number" 
          value={cycleTime} 
          onChange={(e) => setCycleTime(e.target.value)} 
          min="0"  // Definindo o valor mínimo como 0
        />
      </div>
      <div className="item_search">
        <h3>Parada da máquina (segundos)</h3>
        <input 
          type="number" 
          value={stopedMachine} 
          onChange={(e) => setStopedMachine(e.target.value)} 
          min="0"  // Definindo o valor mínimo como 0
        />
      </div>
      
      <div className="item_search">
        <h3>Intervalo de Resumo de Dados (segundos)</h3>
        <input 
          type="number" 
          value={intervaloResumo} 
          onChange={(e) => setintervaloResumo(e.target.value)} 
          min="0"  // Definindo o valor mínimo como 0
        />
      </div>

      

      <div>
        <h2>All Response Data:</h2> 
        <pre style={{ color: 'black', fontSize: '18px' }}>{JSON.stringify(responseData, null, 2)}</pre>
      </div>

    </div>
  );
};

export default OEESetup;
*/