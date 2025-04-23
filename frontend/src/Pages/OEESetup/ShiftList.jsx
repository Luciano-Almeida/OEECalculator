import React from 'react';

const ShiftList = ({ shifts, onEdit, onDelete }) => (
  <ul className="schedule-list">
    {shifts.map((shift) => (
      <li key={shift.tempId || shift.id}>
        <strong>{shift.name}</strong> ({shift.days.join(', ')}): {shift.startTime} - {shift.endTime}
        <button onClick={() => onEdit(shift)}>Editar</button>
        <button onClick={() => onDelete(shift)}>Remover</button>
      </li>
    ))}
  </ul>
);

export default ShiftList;
