import React from 'react';

const daysOfWeek = ['Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado'];

const ShiftForm = ({
  shiftName,
  startTime,
  endTime,
  selectedDays,
  onChange,
  onDayToggle,
  onSubmit,
  isEditing
}) => {
  return (
    <div>
      <label>Nome do Turno</label>
      <input
        style={{width: "100%", padding: '0.5rem', borderRadius: '6px',  border: '1px solid #ccc', fontSize: '0.95rem'}}
        type="text"
        placeholder="Ex: Turno da Manhã"
        value={shiftName}
        onChange={(e) => onChange('shiftName', e.target.value)}
      />

      <div className="oee-time-selectors">
        <div>
          <label>Início</label>
          <input type="time" value={startTime} onChange={(e) => onChange('startTime', e.target.value)} />
        </div>
        <div>
          <label>Fim</label>
          <input type="time" value={endTime} onChange={(e) => onChange('endTime', e.target.value)} />
        </div>
      </div>

      <div className="oee-days">
        {daysOfWeek.map((day, index) => (
          <label key={index} className={`day-checkbox ${selectedDays.includes(day) ? 'active' : ''}`}>
            <input
              type="checkbox"
              checked={selectedDays.includes(day)}
              onChange={() => onDayToggle(day)}
            />
            {day}
          </label>
        ))}
      </div>

      <button className="btn secondary" onClick={onSubmit}>
        {isEditing ? '✏️ Atualizar Turno' : '➕ Adicionar Turno'}
      </button>
    </div>
  );
};

export default ShiftForm;
