import React, { useState } from 'react';
import './TesteOEESetup.css';
import ShiftForm from './ShiftForm';
import ShiftList from './ShiftList';
import { useAuditoria } from '../../hooks/useAuditoria';

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
  const { registrarAuditoria } = useAuditoria();

  const registro = async (action, detalhe) => {
    await registrarAuditoria("TELA OEE SETUP", action, detalhe);
  };
  
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

  const handleAddOrUpdateShift = async () => {
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
    console.log("ADICIONAR TURNO", `Turno: ${shiftName}, Início: ${startTime}, Fim: ${endTime}, Dias: ${selectedDays.join(', ')}`);
    await registro("ADICIONAR TURNO", `Turno: ${shiftName}, Início: ${startTime}, Fim: ${endTime}, Dias: ${selectedDays.join(', ')}`);
  };

  const handleEditShift = (shift) => {
    setShiftName(shift.name);
    setStartTime(shift.startTime);
    setEndTime(shift.endTime);
    setSelectedDays(shift.days);
    setEditingId(shift.tempId);
    console.log("EDITAR TURNO", `Turno editado: ${shift.name}`);
    registro("EDITAR TURNO", `Turno editado: ${shift.name}`);
  };

  const handleDeleteShift = (shift) => {
    setShifts(shifts.filter(s => s.tempId !== shift.tempId));
    registro("EXCLUIR TURNO", `Turno excluído: ${shift.name}`);
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
    registro("SALVAR CONFIGURAÇÃO", `Configuração salva: ${JSON.stringify(config)}`);
    alert('✅ Configuração salva com sucesso!');
  };

  return (
    <div className="oee-container">
      <h2>🛠️ Configuração do OEE</h2>

      {/* Câmera */}
      <section className="oee-section">
        <h3>📷 Tipo de Câmera</h3>
        <select value={cameraType} onChange={async (e) => {
                                        setCameraType(e.target.value);
                                        await registro("ALTERAÇÃO", `Tipo de câmera alterado: ${e.target.value}`);
                                        }}
        >
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
              onChange={async (e) => {
                setCycleTime(e.target.value);
                await registro("ALTERAÇÃO", `Tempo de ciclo alterado para: ${e.target.value} PPM`);
              }}
            />
          </div>
          <div>
            <label>Parada da Máquina (s)</label>
            <input
              type="number"
              placeholder="Segundos"
              value={machineStopTime}
              onChange={async (e) => {
                setMachineStopTime(e.target.value);
                await registro("ALTERAÇÃO", `Tempo de parada da máquina alterado para: ${e.target.value} s`);
              }}
            />
          </div>
          <div>
            <label>Resumo dos Dados (s)</label>
            <input
              type="number"
              placeholder="Segundos"
              value={dataSummaryInterval}
              onChange={async (e) => {
                setDataSummaryInterval(e.target.value);
                await registro("ALTERAÇÃO", `Intervalo de resumo dos dados alterado para: ${e.target.value} s`);
              }}
            />
          </div>
        </div>
      </section>

      <button className="btn primary" onClick={handleSubmit}>💾 Salvar Configuração</button>
    </div>
  );
};

export default TesteOEESetup;

