import React, { useState } from 'react';
import './TesteOEESetup.css';
import ShiftForm from './ShiftForm';
import ShiftList from './ShiftList';

const cameraOptions = [
  { id: 1, name: 'Câmera 1' },
  { id: 2, name: 'Câmera 2' },
  { id: 3, name: 'Câmera 3' },
  { id: 4, name: 'Câmera 4' },
];

const TesteOEESetup = () => {
  const [shifts, setShifts] = useState([]);
  const [shiftName, setShiftName] = useState('');
  const [startTime, setStartTime] = useState('');
  const [endTime, setEndTime] = useState('');
  const [selectedDays, setSelectedDays] = useState([]);
  const [editingId, setEditingId] = useState(null);

  const [cameraType, setCameraType] = useState('');
  const [cameraId, setCameraId] = useState(null);
  const [cycleTime, setCycleTime] = useState('');
  const [machineStopTime, setMachineStopTime] = useState('');
  const [dataSummaryInterval, setDataSummaryInterval] = useState('');

  const [setupId, setSetupId] = useState(null);

  const handleDayToggle = (day) => {
    setSelectedDays((prev) =>
      prev.includes(day) ? prev.filter((d) => d !== day) : [...prev, day]
    );
  };

  const handleFormChange = (field, value) => {
    if (field === 'shiftName') setShiftName(value);
    else if (field === 'startTime') setStartTime(value);
    else if (field === 'endTime') setEndTime(value);
  };

  const handleAddOrUpdateShift = () => {
    if (!shiftName || !startTime || !endTime || selectedDays.length === 0) return;
  
    const orderedDaysOfWeek = ['Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado'];
  
    const newShift = {
      name: shiftName,
      startTime,
      endTime,
      days: [...selectedDays].sort(
        (a, b) => orderedDaysOfWeek.indexOf(a) - orderedDaysOfWeek.indexOf(b)
      ),
      tempId: editingId || Date.now(),
    };
  
    if (editingId) {
      setShifts(shifts.map((s) => (s.tempId === editingId ? newShift : s)));
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
    setShifts(shifts.filter((s) => s.tempId !== shift.tempId));
  };

  const handleCameraChange = async (e) => {
    const selectedId = Number(e.target.value);
    const selectedName = cameraOptions.find((c) => c.id === selectedId)?.name || '';

    setCameraId(selectedId);
    setCameraType(selectedName);

    if (!selectedId) return;

    try {
      const res = await fetch(`http://localhost:8000/oee-setup-by-camera-id/${selectedId}`);
      if (!res.ok) throw new Error('Configuração não encontrada');
      const data = await res.json();

      // Preenchendo os campos automaticamente
      setCycleTime(data.line_speed.toString());
      setMachineStopTime(data.stop_time.toString());
      setDataSummaryInterval(data.digest_time.toString());
      setShifts(
        (data.shifts || []).map((s, index) => ({
          ...s,
          tempId: index + 1,
        }))
      );
      // Se quiser popular outros campos como horário inicial:
      setStartTime(data.start_shift?.split('T')[1]?.slice(0, 5) || '');
      setEndTime(data.stop_shift?.split('T')[1]?.slice(0, 5) || '');
      setSetupId(data.id); // armazenando o ID para depois usar no update
    } catch (error) {
      console.warn('Erro ao buscar configuração:', error.message);
      alert('⚠️ Nenhuma configuração encontrada para esta câmera.');
      // Limpar campos se quiser
    }
  };

  const handleSubmit = async () => {
    const payload = {
      user: 'operador1', // ou outro usuário, caso tenha login
      stop_time: Number(machineStopTime),
      digest_time: Number(dataSummaryInterval),
      line_speed: Number(cycleTime),
      camera_name_id: cameraId,
      shifts: shifts.map(({ tempId, ...shift }) => shift), // removendo tempId
    };
    console.log("payload", payload)
    try {
      if (setupId) {
        const res = await fetch(`http://localhost:8000/update-oee-setup/${setupId}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
  
        if (!res.ok) throw new Error('Erro ao atualizar configuração');
        const updated = await res.json();
        alert('✅ Configuração atualizada com sucesso!');
      } else {
        alert('⚠️ Nenhum setup carregado para atualizar!');
      }
    } catch (err) {
      console.error(err);
      alert('❌ Erro ao salvar a configuração.');
    }
  };
  
  

  return (
    <div className="oee-container">
      <h2>🛠️ Configuração do OEE</h2>

      {/* Câmera */}
      <section className="oee-section">
        <h3>📷 Tipo de Câmera</h3>
        <select value={cameraId || ''} onChange={handleCameraChange}>
          <option value="">Selecione...</option>
          {cameraOptions.map((cam) => (
            <option key={cam.id} value={cam.id}>
              {cam.name}
            </option>
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
