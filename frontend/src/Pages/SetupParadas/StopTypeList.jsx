import React from "react";

const StopTypeList = ({
  types,
  selectedItem,
  onSelect,
  editedValues,
  setEditedValues,
  category
}) => {
  return (
    <ul>
      {types.map((type) => (
        <li
          key={type.id}
          onClick={() => onSelect(type.id, type.name, category)}
          style={{
            cursor: "pointer",
            fontWeight: selectedItem?.id === type.id ? 'bold' : 'normal'
          }}
        >
          {selectedItem?.id === type.id ? (
            <div>
              <input
                type="text"
                value={editedValues.name}
                onChange={(e) => setEditedValues({ ...editedValues, name: e.target.value })}
              />
              {category === "planejada" && (
                <>
                  <input
                    type="time"
                    value={editedValues.startTime}
                    onChange={(e) => setEditedValues({ ...editedValues, startTime: e.target.value })}
                  />
                  <input
                    type="time"
                    value={editedValues.endTime}
                    onChange={(e) => setEditedValues({ ...editedValues, endTime: e.target.value })}
                  />
                </>
              )}
            </div>
          ) : (
            <div>
              {type.name}
              {category === "planejada" && ` - ${type.start_time} - ${type.stop_time}`}
            </div>
          )}
        </li>
      ))}
    </ul>
  );
};

export default StopTypeList;
