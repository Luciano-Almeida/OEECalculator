import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import StopTypeList from "./StopTypeList";
import StopTypeForm from "./StopTypeForm";
import StopTypeActions from "./StopTypeActions";
import "./StopTypesManagement.css";
import { useAuditoria } from "../../hooks/useAuditoria";

const StopTypesManagement = () => {
  const [startTime, setStartTime] = useState('');
  const [endTime, setEndTime] = useState('');

  const [paradasPlanejadasTypes, setParadasPlanejadasTypes] = useState([]);
  const [paradasNaoPlanejadasTypes, setParadasNaoPlanejadasTypes] = useState([]);

  const [newParadaPlanejadaType, setParadasPlanejadaType] = useState("");
  const [newParadaNaoPlanejadaType, setParadasNaoPlanejadaType] = useState("");

  const [selectedPlanejadaItem, setSelectedPlanejadaItem] = useState(null);
  const [selectedNaoPlanejadaItem, setSelectedNaoPlanejadaItem] = useState(null);
  const [editedValues, setEditedValues] = useState({
    name: "",
    startTime: "",
    endTime: "",
  });

  const listRefPlanejada = useRef(null);
  const listRefNaoPlanejada = useRef(null);
  const { registrarAuditoria } = useAuditoria();

  const registro = async (action, detalhe) => {
    await registrarAuditoria("TELA PARADAS SETUP", action, detalhe);
  };

  useEffect(() => {
    fetchParadasPlanejadasSetup();
    fetchParadasNaoPlanejadasSetup();
  }, []);

  const fetchParadasPlanejadasSetup = async () => {
    try {
      const response = await axios.get('http://localhost:8000/get_setup_paradas_planejadas/');
      setParadasPlanejadasTypes(response.data);
      setParadasPlanejadaType("");
      console.log('setup planejadas', response.data);
    } catch (error) {
      console.error("Erro ao carregar paradas planejadas", error);
      registro("ERRO", "Falha ao carregar paradas planejadas");
    }
  };

  const fetchParadasNaoPlanejadasSetup = async () => {
    try {
      const response = await axios.get('http://localhost:8000/get_setup_paradas_nao_planejadas/');
      setParadasNaoPlanejadasTypes(response.data);
      setParadasNaoPlanejadaType("");
      console.log('setup não planejadas', response.data);
    } catch (error) {
      console.error("Erro ao carregar paradas não planejadas", error);
      registro("ERRO", "Falha ao carregar paradas não planejadas");
    }
  };

  const handleAddPlanejadaType = async () => {
    if (newParadaPlanejadaType.trim() && startTime && endTime) {
      const newType = {
        name: newParadaPlanejadaType,
        start_time: startTime, // Garantir que a data seja no formato ISO 8601
        stop_time: endTime,   // Garantir que a data seja no formato ISO 8601
        camera_name_id: 1,
      };
      console.log('newType', newType)
      const response = await axios.post('http://localhost:8000/post_setup_paradas_planejadas/', newType);
      fetchParadasPlanejadasSetup();
      await registro("ADICIONAR PARADA PLANEJADA", `Nome: ${newParadaPlanejadaType}, Início: ${startTime}, Fim: ${endTime}`);
    }
  };

  const handleAddNaoPlanejadaType = async () => {
    if (newParadaNaoPlanejadaType.trim()) {
      const newType = {
        name: newParadaNaoPlanejadaType,
      };
      const response = await axios.post('http://localhost:8000/post_setup_paradas_nao_planejadas/', newType);
      fetchParadasNaoPlanejadasSetup();
      registro("ADICIONAR PARADA NÃO PLANEJADA", `Nome: ${newParadaNaoPlanejadaType}`);
    }
  };

  const handleDelete = async () => {
    const confirmDelete = window.confirm("Você tem certeza que deseja excluir este item?");
    if (!confirmDelete) return;

    if (selectedPlanejadaItem) {
      console.log(`delete Planned /${selectedPlanejadaItem.id}`);
      await axios.delete(`http://localhost:8000/delete_planned_downtime_setup/${selectedPlanejadaItem.id}`);
      fetchParadasPlanejadasSetup();
      setSelectedPlanejadaItem(null);
      registro("EXCLUIR PARADA PLANEJADA", `ID: ${selectedPlanejadaItem.id}, Nome: ${selectedPlanejadaItem.name}`);
    } else if (selectedNaoPlanejadaItem) {
      console.log(`delete Unplanned /${selectedNaoPlanejadaItem.id}`);

      await axios.delete(`http://localhost:8000/delete_unplanned_downtime_setup/${selectedNaoPlanejadaItem.id}`);
      fetchParadasNaoPlanejadasSetup();
      registro("EXCLUIR PARADA NÃO PLANEJADA", `ID: ${selectedNaoPlanejadaItem.id}, Nome: ${selectedNaoPlanejadaItem.name}`);
      setSelectedNaoPlanejadaItem(null);
    }

    setEditedValues({ name: "", startTime: "", endTime: "" });
  };

  const handleSaveEdit = async () => {
    const confirmSave = window.confirm("Você tem certeza que deseja salvar as alterações?");
    if (!confirmSave) return;

    if (selectedPlanejadaItem) {
      const updatedItem = {
        //...selectedPlanejadaItem,
        name: editedValues.name,
        start_time: editedValues.startTime,
        stop_time: editedValues.endTime,
        camera_name_id: 1
      };

      console.log('updatedItem', selectedPlanejadaItem.id, updatedItem)

      await axios.put(`http://localhost:8000/update_planned_downtime_setup/${selectedPlanejadaItem.id}`, updatedItem);
      fetchParadasPlanejadasSetup();
      registro("EDITAR PARADA PLANEJADA", `ID: ${selectedPlanejadaItem.id}, Novo nome: ${editedValues.name}`);
      setSelectedPlanejadaItem(null);
    } else if (selectedNaoPlanejadaItem) {
      const updatedItem = {
        //...selectedNaoPlanejadaItem,
        name: editedValues.name,
      };

      console.log('updatedItem', selectedNaoPlanejadaItem.id, updatedItem)

      const response = await axios.put(`http://localhost:8000/update_unplanned_downtime_setup/${selectedNaoPlanejadaItem.id}`, updatedItem);
      fetchParadasNaoPlanejadasSetup();
      registro("EDITAR PARADA NÃO PLANEJADA", `ID: ${selectedNaoPlanejadaItem.id}, Novo nome: ${editedValues.name}`);
      setSelectedNaoPlanejadaItem(null);
    }

    setEditedValues({ name: "", startTime: "", endTime: "" });
  };

  const handleSelectItem = (id, name, category) => {
    if (category === "planejada") {
      if (selectedPlanejadaItem?.id !== id) {
        const selected = paradasPlanejadasTypes.find((type) => type.id === id);
        if (selected) {
          setEditedValues({
            name: selected.name,
            startTime: selected.start_time,
            endTime: selected.stop_time,
          });
        }
        
        setSelectedPlanejadaItem({ id, name });
        setSelectedNaoPlanejadaItem(null);
        registro("SELECIONAR PARADA PLANEJADA", `ID: ${id}, Nome: ${name}`);
      }
    } else {
      if (selectedNaoPlanejadaItem?.id !== id) {
        const selected = paradasNaoPlanejadasTypes.find((type) => type.id === id);
        setEditedValues({ name: selected.name });
        setSelectedNaoPlanejadaItem({ id, name });
        setSelectedPlanejadaItem(null);
        registro("SELECIONAR PARADA NÃO PLANEJADA", `ID: ${id}, Nome: ${name}`);
      }
    }
  };


  const handleClickOutside = (e) => {
    if (
      listRefPlanejada.current && !listRefPlanejada.current.contains(e.target) &&
      listRefNaoPlanejada.current && !listRefNaoPlanejada.current.contains(e.target)
    ) {
      setSelectedPlanejadaItem(null);
      setSelectedNaoPlanejadaItem(null);
    }
  };

  useEffect(() => {
    document.addEventListener("click", handleClickOutside);
    return () => {
      document.removeEventListener("click", handleClickOutside);
    };
  }, []);

  return (
    <div className="stop-types-management">
      <div className="stop-types-container">
        {/* Planejadas */}
        <div className="stop-types-column" ref={listRefPlanejada}>
          <h2>Paradas Planejadas</h2>
          <StopTypeList
            types={paradasPlanejadasTypes}
            selectedItem={selectedPlanejadaItem}
            onSelect={handleSelectItem}
            editedValues={editedValues}
            setEditedValues={setEditedValues}
            category="planejada"
          />
          <StopTypeForm
            isPlanejada={true}
            newType={newParadaPlanejadaType}
            setNewType={setParadasPlanejadaType}
            startTime={startTime}
            setStartTime={setStartTime}
            endTime={endTime}
            setEndTime={setEndTime}
            onAdd={handleAddPlanejadaType}
          />
          {selectedPlanejadaItem && (
            <StopTypeActions onSave={handleSaveEdit} onDelete={handleDelete} />
          )}
        </div>

        {/* Não Planejadas */}
        <div className="stop-types-column" ref={listRefNaoPlanejada}>
          <h2>Paradas Não Planejadas</h2>
          <StopTypeList
            types={paradasNaoPlanejadasTypes}
            selectedItem={selectedNaoPlanejadaItem}
            onSelect={handleSelectItem}
            editedValues={editedValues}
            setEditedValues={setEditedValues}
            category="não planejada"
          />
          <StopTypeForm
            isPlanejada={false}
            newType={newParadaNaoPlanejadaType}
            setNewType={setParadasNaoPlanejadaType}
            onAdd={handleAddNaoPlanejadaType}
          />
          {selectedNaoPlanejadaItem && (
            <StopTypeActions onSave={handleSaveEdit} onDelete={handleDelete} />
          )}
        </div>
      </div>
    </div>
  );
};

export default StopTypesManagement;



