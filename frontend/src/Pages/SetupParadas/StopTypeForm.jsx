import React from "react";

const StopTypeForm = ({
  isPlanejada,
  newType,
  setNewType,
  startTime,
  setStartTime,
  endTime,
  setEndTime,
  onAdd
}) => {
  return (
    <div className="actions">
      <input
        type="text"
        value={newType}
        onChange={(e) => setNewType(e.target.value)}
        placeholder={`Novo tipo de parada ${isPlanejada ? 'planejada' : 'não planejada'}`}
      />
      {isPlanejada && (
        <>
          <input
            type="time"
            value={startTime}
            onChange={(e) => setStartTime(e.target.value)}
            required
          />
          <input
            type="time"
            value={endTime}
            onChange={(e) => setEndTime(e.target.value)}
            required
          />
        </>
      )}
      <button onClick={onAdd}>Adicionar</button>
    </div>
  );
};

export default StopTypeForm;
