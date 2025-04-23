import React from "react";

const StopTypeActions = ({ onSave, onDelete }) => {
  return (
    <div className="actions">
      <button className="save" onClick={onSave}>Salvar Edição</button>
      <button className="delete" onClick={onDelete}>Excluir</button>
    </div>
  );
};

export default StopTypeActions;

