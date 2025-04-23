
/*
import { useState, useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Select, SelectItem } from "@/components/ui/select";
import { Table } from "@/components/ui/table";

const mockParadas = [
  { id: 1, inicio: "2025-03-17 08:00", fim: "2025-03-17 08:30", tipo: "Não Planejada" },
  { id: 2, inicio: "2025-03-17 09:00", fim: "2025-03-17 09:20", tipo: "Planejada" },
];

const tiposParada = ["Planejada", "Não Planejada Justificada", "Não Planejada Não Justificada"];

export default function OEEParadas() {
  const [paradas, setParadas] = useState(mockParadas);
  const [tipoSelecionado, setTipoSelecionado] = useState({});

  const handleTipoChange = (id, tipo) => {
    setTipoSelecionado((prev) => ({ ...prev, [id]: tipo }));
  };

  const handleSalvar = (id) => {
    setParadas((prev) => prev.map((p) => (p.id === id ? { ...p, tipo: tipoSelecionado[id] } : p)));
  };

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold">Gestão de Paradas</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {paradas.map((p) => (
          <Card key={p.id} className="p-4 shadow-md">
            <CardContent>
              <p className="text-lg font-semibold">Parada #{p.id}</p>
              <p>Início: {p.inicio}</p>
              <p>Fim: {p.fim}</p>
              <p className={`text-sm font-bold ${p.tipo.includes("Não Planejada Não Justificada") ? "text-red-500" : "text-green-600"}`}>Tipo: {p.tipo}</p>
              <Select onChange={(e) => handleTipoChange(p.id, e.target.value)}>
                <option value="">Selecionar Tipo</option>
                {tiposParada.map((tipo, index) => (
                  <SelectItem key={index} value={tipo}>{tipo}</SelectItem>
                ))}
              </Select>
              <Button className="mt-2" onClick={() => handleSalvar(p.id)}>Salvar</Button>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
*/