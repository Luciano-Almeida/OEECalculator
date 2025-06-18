import React, { useState } from 'react';
import './TesteOEESetup.css';
import ShiftForm from './ShiftForm';
import ShiftList from './ShiftList';
import { useAuditoria } from '../../hooks/useAuditoria';

const cameraIds = import.meta.env.VITE_CAMERAS
  ? import.meta.env.VITE_CAMERAS.split(',').map(id => parseInt(id.trim()))
  : [];

const cameraOptions = cameraIds.map(id => ({
  id,
  name: `Câmera ${id}`,
}));

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
  const { registrarAuditoria } = useAuditoria();

  const registro = async (action, detalhe) => {
    await registrarAuditoria("TELA OEE SETUP", action, detalhe);
  };

  const handleDayToggle = (day) => {
    setSelectedDays((prev) =>
      prev.includes(day) ? prev.filter((d) => d !== day) : [...prev, day]
    );
    registro("ALTERAÇÃO", `Dia ${day} ${selectedDays.includes(day) ? "removido" : "adicionado"} do turno`);
  };

  const handleFormChange = (field, value) => {
    if (field === 'shiftName') {
      setShiftName(value);
      registro("ALTERAÇÃO", `Nome do turno alterado para: ${value}`);
    } else if (field === 'startTime') {
      setStartTime(value);
      registro("ALTERAÇÃO", `Horário de início alterado para: ${value}`);
    } else if (field === 'endTime') {
      setEndTime(value);
      registro("ALTERAÇÃO", `Horário de fim alterado para: ${value}`);
    }
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
      registro("EDITAR TURNO", `Turno editado: ${shiftName}`);
    } else {
      setShifts([...shifts, newShift]);
      registro("ADICIONAR TURNO", `Turno: ${shiftName}, Início: ${startTime}, Fim: ${endTime}, Dias: ${selectedDays.join(', ')}`);
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
    registro("EDITAR TURNO", `Turno editado: ${shift.name}`);
  };

  const handleDeleteShift = (shift) => {
    setShifts(shifts.filter((s) => s.tempId !== shift.tempId));
    registro("EXCLUIR TURNO", `Turno excluído: ${shift.name}`);
  };

  const handleCameraChange = async (e) => {
    const selectedId = Number(e.target.value);
    const selectedName = cameraOptions.find((c) => c.id === selectedId)?.name || '';

    setCameraId(selectedId);
    setCameraType(selectedName);
    registro("SELECIONAR CÂMERA", `Câmera selecionada: ${selectedName} (ID ${selectedId})`);

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

      registro("CARREGAR CONFIGURAÇÃO", `Setup carregado para câmera ${selectedName}`);
    } catch (error) {
      console.warn('Erro ao buscar configuração:', error.message);
      alert('⚠️ Nenhuma configuração encontrada para esta câmera.');
      registro("ERRO", `Falha ao carregar configuração para câmera ${selectedName}`);
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
    console.log("payload", payload);
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
        registro("SALVAR CONFIGURAÇÃO", `Setup atualizado com ID: ${setupId}`);
      } else {
        alert('⚠️ Nenhum setup carregado para atualizar!');
        registro("ERRO", "Tentativa de salvar sem setup carregado");
      }
    } catch (err) {
      console.error(err);
      alert('❌ Erro ao salvar a configuração.');
      registro("ERRO", "Falha ao salvar configuração OEE");
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
