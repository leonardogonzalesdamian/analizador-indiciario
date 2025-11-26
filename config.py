# Configuración centralizada del sistema de auditoría indiciaria

# Pesos relativos de cada criterio C1–C7 en el cálculo del ICI global.
# Puedes afinarlos más adelante según tu propio criterio metodológico.
PESOS_CRITERIOS = {
    "C1": 1.5,
    "C2": 1.5,
    "C3": 1.0,
    "C4": 1.0,
    "C5": 2.5,  # Hipótesis alternativas: peso alto
    "C6": 1.0,
    "C7": 2.0,
}


def interpretar_ici(ici: float, criterios: dict) -> str:
    """
    Devuelve una interpretación textual breve del valor del ICI.
    Se tienen en cuenta también algunos umbrales especiales de C5 y C7.
    """
    if ici < 40:
        base = "Riesgo MUY ALTO: la coherencia indiciaria es deficiente o casi inexistente."
    elif ici < 55:
        base = "Riesgo ALTO: la motivación indiciaria presenta fallas relevantes."
    elif ici < 70:
        base = "Riesgo MEDIO: la sentencia tiene una estructura aceptable pero con debilidades."
    elif ici < 85:
        base = "Riesgo BAJO: la motivación indiciaria es, en general, sólida."
    else:
        base = "Riesgo MUY BAJO: la coherencia indiciaria es alta."

    avisos = []

    if criterios.get("C5", 100) < 40:
        avisos.append(
            "C5 muy bajo: no se desarrollan adecuadamente hipótesis alternativas ni se descartan "
            "otras explicaciones razonables de los hechos."
        )

    if criterios.get("C7", 100) < 50:
        avisos.append(
            "C7 bajo: el razonamiento presenta saltos lógicos o contradicciones que dañan la "
            "coherencia global."
        )

    if avisos:
        return base + " " + " ".join(avisos)
    return base
