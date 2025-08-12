import base64
from datetime import datetime
from io import BytesIO
import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from jinja2 import Environment, FileSystemLoader
from PIL import Image
from pydantic import BaseModel
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import templates.auxiliar_functions_pdf_1 as pdf1
from weasyprint import CSS, HTML


# Logger específico
logger = logging.getLogger(__name__)

router = APIRouter()

class Payload(BaseModel):
    imagens: list[str]
    camera_name: str = "—"
    user: str = "—"
    data: list[dict] = []
    type_of_pdf: int = 1

def redimensionar_base64(imagem_base64: str, largura_max=600) -> str:
    # Decodifica a imagem base64 para bytes
    img_data = base64.b64decode(imagem_base64.split(',')[-1])
    img = Image.open(BytesIO(img_data))

    # Calcula nova altura proporcional à nova largura
    largura_original, altura_original = img.size
    if largura_original <= largura_max:
        return imagem_base64  # já está pequena o suficiente

    proporcao = altura_original / largura_original
    nova_altura = int(largura_max * proporcao)

    # Redimensiona
    img = img.resize((largura_max, nova_altura), Image.LANCZOS)


    # Converte de volta para base64
    buffer = BytesIO()
    img.save(buffer, format="PNG")  # ou JPEG
    base64_redimensionada = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{base64_redimensionada}"

def type_of_pdf_1(payload, request):
    def tratamento_de_dados_pdf_1(dados):
        divs = []
        divs.append(pdf1.medias_oee(dados))
        divs.append("<div>  </div>")
        divs.append(pdf1.total_producao(dados))
        divs.append(pdf1.resumo_paradas(dados))

        return divs
    
    def lista_de_larguras():
        larguras = [700, 700, 700, 700]
        return larguras

    now = datetime.now()
    divs = tratamento_de_dados_pdf_1(payload.data)
    list_weights = lista_de_larguras()

    # Verificar se ambas as listas têm o mesmo tamanho
    if len(payload.imagens) != len(list_weights) or len(payload.imagens) != len(divs):
        raise ValueError(f"Quantidade de imagens ({len(payload.imagens)}) difere da quantidade de pesos ({len(list_weights)}) ou textos ({len(divs)}).")

    # Redimensiona todas as imagens
    imagens_redimensionadas = [redimensionar_base64(img, weight) for img, weight in zip(payload.imagens, list_weights)]

    # Mover a última imagem (índice -1) para a posição 2 (índice 1)
    penultima_imagem = imagens_redimensionadas.pop(-2)  # remove a última imagem
    imagens_redimensionadas.insert(1, penultima_imagem)  # insere na posição 2 (índice 1)

    dados_para_html = list(zip(imagens_redimensionadas, divs))

    context = {
        "date_str": now.strftime("%d/%m/%Y %H:%M"),
        "usuario": payload.user,
        "camera_name": payload.camera_name,
        "imagens": imagens_redimensionadas,
        "dados": dados_para_html
    }
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("report.html")
    html = template.render(**context)

    #css = CSS(string=open("templates/report.css", encoding="utf‑8").read()) if False else CSS(string="")
    css = CSS(string=open("templates/report.css", encoding="utf-8").read())
    #css = CSS(string="")
    pdf_bytes = HTML(string=html, base_url=str(request.base_url)).write_pdf(stylesheets=[css])

    return pdf_bytes

# 📌 READ
@router.post("/exportar-pdf")
async def exportar_pdf(payload: Payload, request: Request):
    print(f"@@@@@@@@@@----payload.data {payload.data}")
    # gerenciando types
    match payload.type_of_pdf:
        case 1: 
            pdf_bytes = type_of_pdf_1(payload, request)
        case _:
            raise HTTPException(status_code=400, detail="Tipo de PDF inválido.")
    
    

    buffer = BytesIO(pdf_bytes)
    buffer.seek(0)
    return StreamingResponse(buffer, media_type="application/pdf", headers={
        "Content-Disposition": "attachment; filename=relatorio_oee.pdf"
    })

# 📌 CREATE


# 📌 DELETE


# 📌 UPDATE
