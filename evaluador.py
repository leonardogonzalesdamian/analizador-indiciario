import re
from typing import Dict, Any

from config import PESOS_CRITERIOS, interpretar_ici


def _contar(patrones, texto: str) -> int:
    """Cuenta ocurrencias totales de una lista de patrones regex en el texto."""
    total = 0
    for patron in patrones:
        total += len(re.findall(patron, texto, flags=re.IGNORECASE))
    return total


def _puntuar_por_frecuencia(n: int, umbral_alto: int, umbral_medio: int, umbral_bajo: int) -> int:
    """
    Devuelve una puntuación cualitativa (0–100) en función del número de ocurrencias n.
    """
    if n >= umbral_alto:
        return 90
    if n >= umbral_medio:
        return 75
    if n >= umbral_bajo:
        return 55
    if n > 0:
        return 35
    return 10


# ----------------- Criterio por criterio ----------------- #

def evaluar_C1(texto: str) -> int:
    """
    C1: Existencia clara de INDICIOS / HECHOS BASE.
    """
    patrones = [
        r"\bindicio[s]?\b",
        r"hecho[s]?\s+base",
        r"hecho[s]?\s+indiciario[s]?",
        r"indiciari[oa]s?",
    ]
    n = _contar(patrones, texto)
    return _puntuar_por_frecuencia(n, umbral_alto=20, umbral_medio=10, umbral_bajo=3)


def evaluar_C2(texto: str) -> int:
    """
    C2: Fiabilidad y claridad de las FUENTES DE INFORMACIÓN.
    """
    patrones = [
        r"\btestig[oa]s?\b",
        r"\bdeclaraci[oó]n\b",
        r"\bpericia[l]?\b",
        r"\bperit[oa]s?\b",
        r"\bacta\b",
        r"\binforme\b",
        r"\bpericial\b",
        r"\bdocumental\b",
    ]
    n = _contar(patrones, texto)
    return _puntuar_por_frecuencia(n, umbral_alto=40, umbral_medio=20, umbral_bajo=8)


def evaluar_C3(texto: str) -> int:
    """
    C3: Existencia de una CADENA LÓGICA EXPLÍCITA entre indicios y conclusión.
    """
    patrones = [
        r"por tanto",
        r"por consiguiente",
        r"en consecuencia",
        r"por ello",
        r"de lo expuesto",
        r"de tal manera que",
        r"de modo que",
        r"as[ií]\s+las cosas",
    ]
    n = _contar(patrones, texto)
    return _puntuar_por_frecuencia(n, umbral_alto=25, umbral_medio=12, umbral_bajo=5)


def evaluar_C4(texto: str) -> int:
    """
    C4: Uso de REGLAS DE EXPERIENCIA o máximas de la lógica y de la experiencia.
    """
    patrones = [
        r"reglas?\s+de\s+la\s+experiencia",
        r"m[aá]ximas?\s+de\s+experiencia",
        r"normalmente",
        r"usualmente",
        r"lo habitual es",
        r"suele ocurrir que",
    ]
    n = _contar(patrones, texto)
    return _puntuar_por_frecuencia(n, umbral_alto=10, umbral_medio=5, umbral_bajo=2)


def evaluar_C5(texto: str) -> int:
    """
    C5: Consideración de HIPÓTESIS ALTERNATIVAS.
    Es un criterio especialmente sensible: su omisión afecta fuertemente al ICI global.
    """
    patrones = [
        r"otra\s+hip[oó]tesis",
        r"hip[oó]tesis\s+alternativa",
        r"versi[oó]n\s+alternativa",
        r"otra\s+explicaci[oó]n",
        r"no\s+se\s+descarta",
        r"no\s+puede\s+descartarse",
        r"podr[ií]a\s+pensarse",
        r"otras?\s+posibilidades",
    ]
    n = _contar(patrones, texto)
    # Más severo a propósito
    if n == 0:
        return 15
    if n == 1:
        return 30
    if n <= 3:
        return 45
    if n <= 6:
        return 60
    return 80


def evaluar_C6(texto: str) -> int:
    """
    C6: Tratamiento del ESTÁNDAR PROBATORIO y la presunción de inocencia.
    """
    patrones = [
        r"duda\s+razonable",
        r"m[aá]s\s+all[aá]\s+de\s+toda\s+duda",
        r"certeza\s+(m[aá]s\s+all[aá]\s+de\s+la\s+duda)?",
        r"presunci[oó]n\s+de\s+inocencia",
        r"in\s+dubio\s+pro\s+reo",
        r"sospecha\s+razonable",
    ]
    n = _contar(patrones, texto)
    return _puntuar_por_frecuencia(n, umbral_alto=8, umbral_medio=4, umbral_bajo=1)


def evaluar_C7(texto: str) -> int:
    """
    C7: Coherencia GLOBAL del razonamiento.
    """
    conectores_cambio = _contar(
        [r"sin embargo", r"no obstante", r"pero\s+que"], texto
    )
    conectores_cierre = _contar(
        [r"por tanto", r"por consiguiente", r"en consecuencia", r"por ello"], texto
    )

    if conectores_cierre == 0 and conectores_cambio > 10:
        # Muchos giros sin cierre argumental claro
        return 40

    n = conectores_cierre + max(0, 5 - conectores_cambio)
    return _puntuar_por_frecuencia(n, umbral_alto=20, umbral_medio=10, umbral_bajo=4)


# ----------------- Evaluación global ----------------- #

def evaluar_texto(texto: str) -> Dict[str, Any]:
    """
    Evalúa un texto completo y devuelve:
      - criterios: dict con C1–C7
      - ici_global: ICI ajustado (0–100)
      - ici_sin_penalizacion: ICI sin castigo adicional por C5 bajo
      - interpretacion: texto breve en español
    """
    texto = texto or ""
    criterios = {
        "C1": evaluar_C1(texto),
        "C2": evaluar_C2(texto),
        "C3": evaluar_C3(texto),
        "C4": evaluar_C4(texto),
        "C5": evaluar_C5(texto),
        "C6": evaluar_C6(texto),
        "C7": evaluar_C7(texto),
    }

    # ICI sin penalización: promedio ponderado clásico
    suma_pesos = sum(PESOS_CRITERIOS.values())
    ici_sin_penalizacion = 0.0
    for clave, valor in criterios.items():
        peso = PESOS_CRITERIOS.get(clave, 1.0)
        ici_sin_penalizacion += peso * valor
    ici_sin_penalizacion /= suma_pesos

    # Penalización por C5 bajo (hipótesis alternativas)
    if criterios["C5"] < 40:
        ici_global = ici_sin_penalizacion * 0.85
    else:
        ici_global = ici_sin_penalizacion

    interpretacion = interpretar_ici(ici_global, criterios)

    return {
        "criterios": criterios,
        "ici_global": ici_global,
        "ici_sin_penalizacion": ici_sin_penalizacion,
        "interpretacion": interpretacion,
    }
