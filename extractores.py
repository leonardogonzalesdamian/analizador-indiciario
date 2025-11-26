import re
from typing import Optional

import pdfplumber
from docx import Document


def limpiar_texto(texto: Optional[str]) -> str:
    """
    Limpia el texto: elimina espacios duplicados, saltos excesivos y normaliza algunas cosas.
    """
    if not texto:
        return ""
    # Sustituimos saltos de línea múltiples por uno solo
    texto = re.sub(r"\r\n", "\n", texto)
    texto = re.sub(r"\n{3,}", "\n\n", texto)
    # Espacios repetidos
    texto = re.sub(r"[ \t]{2,}", " ", texto)
    return texto.strip()


def leer_pdf(archivo) -> str:
    """
    Lee un PDF (subido vía Streamlit) y devuelve todo el texto concatenado.
    No se limita a las primeras páginas.
    """
    texto_total = []
    with pdfplumber.open(archivo) as pdf:
        for pagina in pdf.pages:
            try:
                contenido = pagina.extract_text() or ""
            except Exception:
                contenido = ""
            if contenido:
                texto_total.append(contenido)
    return "\n\n".join(texto_total)


def leer_word(archivo) -> str:
    """
    Lee un archivo .docx y concatena el texto de todos los párrafos.
    """
    doc = Document(archivo)
    partes = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n\n".join(partes)
