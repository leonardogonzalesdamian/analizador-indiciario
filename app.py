import streamlit as st
from io import StringIO

from extractores import leer_pdf, leer_word, limpiar_texto
from evaluador import evaluar_texto

st.set_page_config(
    page_title="Sistema de Auditoría Indiciaria (ICI) – Versión 2",
    layout="wide"
)

st.title("Sistema de Auditoría Indiciaria (ICI) – Versión 2")
st.caption(
    "Herramienta experimental para evaluar la calidad del razonamiento indiciario en sentencias, "
    "basada en criterios C1–C7 y en un Índice de Coherencia Indiciaria (ICI) ponderado."
)

# -------------------------------------------------------------------
# Entrada de datos
# -------------------------------------------------------------------
opcion = st.radio(
    "Seleccione cómo ingresará el documento a analizar:",
    ("Pegar texto", "Subir PDF", "Subir Word (.docx)"),
    horizontal=True,
)

texto = ""

if opcion == "Pegar texto":
    texto = st.text_area(
        "Pegue aquí el texto completo de la sentencia, requerimiento o resolución",
        height=300,
        placeholder="Pegue el texto íntegro, incluyendo hechos, fundamentos y parte resolutiva…",
    )

elif opcion == "Subir PDF":
    archivo_pdf = st.file_uploader(
        "Suba un archivo PDF (sentencia o requerimiento en versión pura)",
        type=["pdf"],
    )
    if archivo_pdf is not None:
        try:
            texto = leer_pdf(archivo_pdf)
            st.success("PDF cargado correctamente. Se ha extraído el texto completo.")
            with st.expander("Ver texto extraído (solo vista previa)"):
                st.write(texto[:4000] + ("…" if len(texto) > 4000 else ""))
        except Exception as e:
            st.error(f"No se pudo leer el PDF: {e}")

elif opcion == "Subir Word (.docx)":
    archivo_word = st.file_uploader(
        "Suba un archivo de Word (.docx)",
        type=["docx"],
    )
    if archivo_word is not None:
        try:
            texto = leer_word(archivo_word)
            st.success("Documento Word cargado correctamente.")
            with st.expander("Ver texto extraído (solo vista previa)"):
                st.write(texto[:4000] + ("…" if len(texto) > 4000 else ""))
        except Exception as e:
            st.error(f"No se pudo leer el archivo de Word: {e}")

texto = limpiar_texto(texto)

# -------------------------------------------------------------------
# Botón de análisis
# -------------------------------------------------------------------
st.markdown("---")
if st.button("Analizar coherencia indiciaria (C1–C7)"):
    if not texto.strip():
        st.warning("Por favor, ingrese o cargue primero el texto de la resolución.")
    else:
        with st.spinner("Procesando texto y evaluando criterios C1–C7…"):
            resultados = evaluar_texto(texto)

        criterios = resultados["criterios"]
        ici = resultados["ici_global"]
        interpretacion = resultados["interpretacion"]
        ici_sin_penalizacion = resultados["ici_sin_penalizacion"]

        st.subheader("Resultados por criterio (C1–C7)")
        st.json(criterios)

        st.subheader("Índice de Coherencia Indiciaria (ICI) global")
        cols = st.columns(3)
        cols[0].metric("ICI ajustado", f"{ici:.2f}")
        cols[1].metric("ICI sin penalización por C5", f"{ici_sin_penalizacion:.2f}")
        cols[2].metric("C5", f"{criterios['C5']:.0f}")

        st.write("**Interpretación:**", interpretacion)

        st.info(
            "Nota metodológica: esta Versión 2 aplica una penalización adicional cuando el criterio "
            "C5 (hipótesis alternativas) es inferior a 40 puntos. "
            "La idea es reflejar que una grave omisión en C5 afecta de forma decisiva la validez "
            "de toda la inferencia indiciaria."
        )
