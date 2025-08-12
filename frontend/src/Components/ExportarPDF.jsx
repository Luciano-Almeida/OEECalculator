import React from "react";
import html2canvas from "html2canvas";
import axios from "axios";

const ExportarPDF = ({ containerId, cameraName, Usuario, Data, TypeOfPDF }) => {
  const exportar = async () => {
    const container = document.getElementById(containerId);
    if (!container) return alert("Container não encontrado.");

    const chartEls = container.querySelectorAll(".grafico-exportavel");
    const imagens = [];

    for (const el of chartEls) {
      const canvas = await html2canvas(el, { scale: 2 });
      imagens.push(canvas.toDataURL("image/png"));
    }

    try {
      const resp = await axios.post(
        "http://localhost:8000/exportar-pdf",
        {
          imagens,
          camera_name: cameraName,
          user: Usuario,
          data: Data, 
          type_of_pdf: TypeOfPDF
        },
        { responseType: "blob" }
      );

      const blob = new Blob([resp.data], { type: "application/pdf" });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "relatorio_oee.pdf";
      a.click();
    } catch (err) {
      console.error("Erro ao exportar PDF:", err);
      alert("Erro ao exportar PDF.");
    }
  };

  return (
    <button onClick={exportar}>
      Exportar PDF
    </button>
  );
};

export default ExportarPDF;
