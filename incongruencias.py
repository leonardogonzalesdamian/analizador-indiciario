# incongruencias.py
"""
Módulo A – Detector objetivo de incongruencias lógicas y normativas
en resoluciones que usan razonamiento indiciario.

Incluye:
- Reglas generales (duda vs certeza, sospecha, etc.)
- REGLAS 1 a 9 sobre método indiciario.
"""

import re
from typing import List, Dict, Any


# -------------------
# 1. Segmentación y utilidades
# -------------------

def segmentar_parrafos(texto: str) -> List[Dict[str, Any]]:
    """
    Divide el texto en "párrafos" usando doble salto de línea.
    """
    bloques = re.split(r"\n\s*\n", texto)
    parrafos = []
    for i, bloque in enumerate(bloques, start=1):
        limpio = bloque.strip()
        if limpio:
            parrafos.append({"n": i, "texto": limpio})
    return parrafos


def recortar_texto(texto: str, max_len: int = 280) -> str:
    """
    Recorta texto para mostrar como extracto.
    """
    t = texto.strip().replace("\n", " ")
    if len(t) <= max_len:
        return t
    return t[: max_len - 3] + "..."


# -------------------
# 2. Patrones globales
# -------------------

# Duda probatoria
PATRON_DUDA = re.compile(
    r"(no existe prueba suficiente|no se ha acreditado|no se ha demostrado|"
    r"no se ha probado|no se cuenta con prueba suficiente|no hay elementos suficientes)",
    flags=re.IGNORECASE,
)

# Certeza / acreditación plena
PATRON_CERTEZA = re.compile(
    r"(ha quedado acreditado|se encuentra plenamente probado|"
    r"plena certeza|se ha demostrado de manera fehaciente|"
    r"plenamente demostrado)",
    flags=re.IGNORECASE,
)

# Hipótesis alternativas no descartadas
PATRON_NO_DESCARTA_ALT = re.compile(
    r"(no se descartan otras versiones|no se descartan otras hipótesis|"
    r"no puede descartarse|no puede excluirse|no se ha descartado la versión del imputado)",
    flags=re.IGNORECASE,
)

# Única explicación / única conclusión
PATRON_UNICA_EXPLICACION = re.compile(
    r"(única explicación posible|única explicación razonable|"
    r"única conclusión posible|la única hipótesis plausible|"
    r"la única explicación atendible)",
    flags=re.IGNORECASE,
)

# Estándar de sospecha
PATRON_SOSPECHA_SIMPLE = re.compile(
    r"(sospecha simple|mera sospecha|sospecha inicial)",
    flags=re.IGNORECASE,
)

PATRON_SOSPECHA_GRAVE = re.compile(
    r"(sospecha grave|sospecha reveladora)",
    flags=re.IGNORECASE,
)

# ---------- PATRONES ESPECÍFICOS PARA INDICIOS (REGLA 1) ----------

PATRON_INDICIO = re.compile(
    r"\bindicio\b|\bindicios\b|\bhecho indiciario\b|\bhechos indiciarios\b|\bhecho base\b",
    flags=re.IGNORECASE,
)

PATRON_FUENTE_FUERTE = re.compile(
    r"\bpericia\b|\binforme pericial\b|\bperito\b|\binforme t[eé]cnico\b|\bdictamen\b|\bpericia oficial\b",
    flags=re.IGNORECASE,
)

PATRON_FUENTE_DEBIL = re.compile(
    r"\btestigo\b|\bdeclaraci[oó]n\b|\bmanifestaci[oó]n\b|\bversi[oó]n del imputado\b",
    flags=re.IGNORECASE,
)

PATRON_CONJUNTO = re.compile(
    r"(en su conjunto|considerados en su conjunto|"
    r"valorados en conjunto|en forma conjunta|en conjunto permiten concluir|"
    r"indicios convergentes|coherentes entre s[ií])",
    flags=re.IGNORECASE,
)

# ---------- REGLA 2 – Evaluación del indicio ----------

PATRON_EVAL_DEBIL_INDICIO = re.compile(
    r"((indicio|prueba|elemento|medio de prueba).{0,80}"
    r"(no es concluyente|no resulta concluyente|no es determinante|no es suficiente|"
    r"es d[eé]bil|tiene escaso valor|poca fuerza acreditativa|no permite afirmar|"
    r"solo sugiere|aporta poco|limitado alcance probatorio))",
    flags=re.IGNORECASE | re.DOTALL,
)

PATRON_EVAL_FUERTE_INDICIO = re.compile(
    r"((indicio|prueba|elemento|medio de prueba).{0,80}"
    r"(es contundente|resulta contundente|es concluyente|resulta concluyente|"
    r"es determinante|resulta determinante|es rotundo|inequ[ií]voco|"
    r"de singular fuerza acreditativa|permite afirmar sin duda|"
    r"permite tener por cierto|permite tener por plenamente acreditado))",
    flags=re.IGNORECASE | re.DOTALL,
)


# -------------------
# 3. Etiquetado de párrafos
# -------------------

def etiquetar_parrafos(parrafos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    etiquetados = []
    for p in parrafos:
        t = p["texto"]
        etiquetados.append(
            {
                "n": p["n"],
                "texto": t,
                "duda": bool(PATRON_DUDA.search(t)),
                "certeza": bool(PATRON_CERTEZA.search(t)),
                "no_descarta_alt": bool(PATRON_NO_DESCARTA_ALT.search(t)),
                "unica_explicacion": bool(PATRON_UNICA_EXPLICACION.search(t)),
                "sospecha_simple": bool(PATRON_SOSPECHA_SIMPLE.search(t)),
                "sospecha_grave": bool(PATRON_SOSPECHA_GRAVE.search(t)),
                # Método indiciario:
                "tiene_indicio": bool(PATRON_INDICIO.search(t)),
                "fuente_fuerte": bool(PATRON_FUENTE_FUERTE.search(t)),
                "fuente_debil": bool(PATRON_FUENTE_DEBIL.search(t)),
                # Evaluación del indicio:
                "eval_ind_debil": bool(PATRON_EVAL_DEBIL_INDICIO.search(t)),
                "eval_ind_fuerte": bool(PATRON_EVAL_FUERTE_INDICIO.search(t)),
            }
        )
    return etiquetados


# -------------------
# 4. Reglas de incongruencia
# -------------------

def detectar_incongruencias(parrafos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    resultados: List[Dict[str, Any]] = []

    texto_global = " ".join(p["texto"] for p in parrafos)

    con_duda = [p for p in parrafos if p["duda"]]
    con_certeza = [p for p in parrafos if p["certeza"]]
    con_no_descarta = [p for p in parrafos if p["no_descarta_alt"]]
    con_unica = [p for p in parrafos if p["unica_explicacion"]]
    con_sospecha_simple = [p for p in parrafos if p["sospecha_simple"]]
    con_sospecha_grave = [p for p in parrafos if p["sospecha_grave"]]
    con_indicio = [p for p in parrafos if p["tiene_indicio"]]
    con_eval_debil = [p for p in parrafos if p["eval_ind_debil"]]
    con_eval_fuerte = [p for p in parrafos if p["eval_ind_fuerte"]]

    # --------------------------------------------------
    # 4.0 Reglas generales (duda vs certeza, sospecha)
    # --------------------------------------------------

    # 4.0.1 Contradicción duda vs certeza
    if con_duda and con_certeza:
        max_pares = 3
        count = 0
        for pd in con_duda:
            for pc in con_certeza:
                if count >= max_pares:
                    break
                resultados.append(
                    {
                        "tipo": "Contradicción duda vs certeza",
                        "parrafos": [pd["n"], pc["n"]],
                        "detalle": (
                            "En un párrafo se afirma insuficiencia probatoria y en otro certeza plena, "
                            "sin justificar la transición."
                        ),
                        "extractos": [
                            recortar_texto(pd["texto"]),
                            recortar_texto(pc["texto"]),
                        ],
                    }
                )
                count += 1
            if count >= max_pares:
                break

    # 4.0.2 Incongruencia en hipótesis alternativas
    if con_no_descarta and con_unica:
        max_pares = 3
        count = 0
        for pa in con_no_descarta:
            for pu in con_unica:
                if count >= max_pares:
                    break
                resultados.append(
                    {
                        "tipo": "Incongruencia en hipótesis alternativas",
                        "parrafos": [pa["n"], pu["n"]],
                        "detalle": (
                            "Se afirma que no se descartan hipótesis alternativas, "
                            "pero a la vez se sostiene que existe una única explicación."
                        ),
                        "extractos": [
                            recortar_texto(pa["texto"]),
                            recortar_texto(pu["texto"]),
                        ],
                    }
                )
                count += 1
            if count >= max_pares:
                break

    # 4.0.3 Referencia a sospecha simple
    if con_sospecha_simple:
        for ps in con_sospecha_simple:
            resultados.append(
                {
                    "tipo": "Referencia a 'sospecha simple' o equivalente",
                    "parrafos": [ps["n"]],
                    "detalle": (
                        "Se menciona 'sospecha simple' o equivalente; debe verificarse su compatibilidad "
                        "con el estándar exigido en la resolución (p. ej., prisión preventiva)."
                    ),
                    "extractos": [recortar_texto(ps["texto"])],
                }
            )

    # 4.0.4 Tensión entre sospecha simple y grave
    if con_sospecha_simple and con_sospecha_grave:
        resultados.append(
            {
                "tipo": "Tensión entre 'sospecha simple' y 'sospecha grave'",
                "parrafos": [p["n"] for p in con_sospecha_simple + con_sospecha_grave],
                "detalle": (
                    "En distintos párrafos se menciona tanto 'sospecha simple' "
                    "como 'sospecha grave', lo que exige clarificación del estándar aplicado."
                ),
                "extractos": [
                    recortar_texto(p["texto"]) for p in con_sospecha_simple + con_sospecha_grave
                ],
            }
        )

    # ============================================================
    #  REGLA 1 – Pluralidad y convergencia de indicios
    # ============================================================

    parrafos_con_indicio = con_indicio

    # 1.1 Ausencia total de referencia a indicios
    if len(parrafos_con_indicio) == 0 and parrafos:
        resultados.append({
            "tipo": "Ausencia de referencia explícita a indicios o hechos indiciarios",
            "parrafos": [p["n"] for p in parrafos[:3]],
            "detalle": (
                "No se identifican menciones a indicios o hechos indiciarios, pese a tratarse "
                "de una resolución que pretende utilizar razonamiento indiciario."
            ),
            "extractos": [recortar_texto(p["texto"]) for p in parrafos[:3]],
        })

    # 1.2 Indicio único débil
    if len(parrafos_con_indicio) == 1:
        unico = parrafos_con_indicio[0]
        if unico["fuente_debil"] and not unico["fuente_fuerte"]:
            resultados.append({
                "tipo": "Indicio único sin singular fuerza acreditativa",
                "parrafos": [unico["n"]],
                "detalle": (
                    "El único indicio identificado proviene de fuente testimonial débil y "
                    "se presenta como suficiente, vulnerando el método indiciario."
                ),
                "extractos": [recortar_texto(unico["texto"])],
            })

    # 1.3 Pluralidad sin convergencia
    if len(parrafos_con_indicio) >= 2:
        hay_convergencia = bool(PATRON_CONJUNTO.search(texto_global))
        if not hay_convergencia:
            resultados.append({
                "tipo": "Pluralidad de indicios sin explicación de convergencia/interrelación",
                "parrafos": [p["n"] for p in parrafos_con_indicio],
                "detalle": (
                    "Existen varios indicios pero sin valoración conjunta o convergente."
                ),
                "extractos": [recortar_texto(p["texto"]) for p in parrafos_con_indicio[:4]],
            })

    # ============================================================
    #  REGLA 2 – Consistencia interna del indicio
    # ============================================================

    # 2.1 mismo párrafo: fuerte + débil
    for p in parrafos:
        if p["eval_ind_debil"] and p["eval_ind_fuerte"]:
            resultados.append({
                "tipo": "Valoración interna contradictoria del indicio (mismo párrafo)",
                "parrafos": [p["n"]],
                "detalle": (
                    "En un mismo párrafo se califica un indicio como débil y fuerte a la vez."
                ),
                "extractos": [recortar_texto(p["texto"])],
            })

    # 2.2 entre párrafos distintos
    if con_eval_debil and con_eval_fuerte:
        max_pares = 3
        count = 0
        for pd in con_eval_debil:
            for pf in con_eval_fuerte:
                if pd["n"] == pf["n"]:
                    continue
                if count >= max_pares:
                    break
                resultados.append({
                    "tipo": "Evaluación contradictoria del indicio (párrafos distintos)",
                    "parrafos": [pd["n"], pf["n"]],
                    "detalle": (
                        "En un párrafo se describe un indicio como débil y en otro como fuerte o concluyente."
                    ),
                    "extractos": [recortar_texto(pd["texto"]), recortar_texto(pf["texto"])],
                })
                count += 1
            if count >= max_pares:
                break

    # ============================================================
    #  REGLA 3 – Consistencia externa entre indicios
    # ============================================================

    PATRON_CONTRADICCION_INDICIOS = re.compile(
        r"(no coincide con|contradice|incompatible con|no guarda relaci[oó]n|"
        r"no se relaciona|resulta incompatible|es inconsistente con|se opone a|discrepa)",
        flags=re.IGNORECASE,
    )

    for p in parrafos_con_indicio:
        if PATRON_CONTRADICCION_INDICIOS.search(p["texto"]):
            resultados.append({
                "tipo": "Contradicción explícita entre indicios",
                "parrafos": [p["n"]],
                "detalle": "Se explicita incompatibilidad entre indicios o hechos indiciarios.",
                "extractos": [recortar_texto(p["texto"])],
            })

    patron_conexion = re.compile(
        r"(relaci[oó]n l[oó]gica|conexi[oó]n|v[ií]nculo|enlace|coherencia externa|armoniza)",
        flags=re.IGNORECASE,
    )

    if len(parrafos_con_indicio) >= 2 and not patron_conexion.search(texto_global):
        resultados.append({
            "tipo": "Falta de conexión entre indicios (consistencia externa)",
            "parrafos": [p["n"] for p in parrafos_con_indicio],
            "detalle": "Los indicios no aparecen conectados ni articulados entre sí.",
            "extractos": [recortar_texto(p["texto"]) for p in parrafos_con_indicio[:4]],
        })

    # ============================================================
    #  REGLA 4 – Saltos lógicos típicos
    # ============================================================

    patron_presencia = re.compile(
        r"(por el solo hecho de encontrarse|por el solo hecho de estar|basta la presencia|por estar en el lugar)",
        flags=re.IGNORECASE,
    )
    patron_conocimiento_r4 = re.compile(
        r"(deb[ií]a conocer|sab[ií]a|no pod[ií]a ignorar|ten[ií]a conocimiento)",
        flags=re.IGNORECASE,
    )

    for p in parrafos:
        texto_p = p["texto"]
        if patron_presencia.search(texto_p) and patron_conocimiento_r4.search(texto_p):
            resultados.append({
                "tipo": "Salto presencia física → conocimiento/participación",
                "parrafos": [p["n"]],
                "detalle": "Se infiere conocimiento o participación solo desde la presencia física.",
                "extractos": [recortar_texto(texto_p)],
            })

    patron_cargo = re.compile(
        r"(por su calidad de|en su condici[oó]n de|en su calidad de|por su cargo de)",
        flags=re.IGNORECASE,
    )
    patron_responsab = re.compile(
        r"(es responsable|dirig[ií]a|orden[oó]|autoriz[oó]|dispuso|ten[ií]a dominio del hecho)",
        flags=re.IGNORECASE,
    )

    for p in parrafos:
        texto_p = p["texto"]
        if patron_cargo.search(texto_p) and patron_responsab.search(texto_p):
            resultados.append({
                "tipo": "Salto de cargo/jerarquía → autoría/responsabilidad penal",
                "parrafos": [p["n"]],
                "detalle": "Se deduce autoría o responsabilidad penal solo por el cargo.",
                "extractos": [recortar_texto(texto_p)],
            })

    patron_conclusion_fuerte = re.compile(
        r"(es evidente que|resulta evidente que|no cabe duda de que|"
        r"resulta incuestionable que|es indudable que)",
        flags=re.IGNORECASE,
    )
    patron_referencia_prueba = re.compile(
        r"(prueba|pruebas|indicio|indicios|hecho indiciario|hechos indiciarios|"
        r"pericia|perito|informe pericial|informe t[eé]cnico|"
        r"testigo|testigos|declaraci[oó]n|declaraciones|acta|actas|informe)",
        flags=re.IGNORECASE,
    )

    for p in parrafos:
        texto_p = p["texto"]
        if patron_conclusion_fuerte.search(texto_p) and not patron_referencia_prueba.search(texto_p):
            resultados.append(
                {
                    "tipo": "Conclusión categórica sin referencia explícita a prueba/indicios",
                    "parrafos": [p["n"]],
                    "detalle": (
                        "Se formulan conclusiones categóricas sin mencionar pruebas o indicios de soporte."
                    ),
                    "extractos": [recortar_texto(texto_p)],
                }
            )

    # ============================================================
    #  REGLA 5 – Uso indebido de testimoniales
    # ============================================================

    patron_testimonio = re.compile(
        r"(testigo|declaraci[oó]n|manifestaci[oó]n|versi[oó]n del imputado)",
        flags=re.IGNORECASE,
    )
    patron_fuerza_indebida = re.compile(
        r"(indicio contundente|prueba concluyente|prueba determinante|"
        r"prueba inequ[ií]voca|permite tener por acreditado|"
        r"demuestra claramente|acredita fehacientemente)",
        flags=re.IGNORECASE,
    )

    for p in parrafos:
        texto_p = p["texto"]
        if patron_testimonio.search(texto_p) and patron_fuerza_indebida.search(texto_p):
            resultados.append({
                "tipo": "Uso indebido de testimonial como indicio fuerte",
                "parrafos": [p["n"]],
                "detalle": (
                    "Una fuente testimonial es presentada como prueba concluyente o contundente."
                ),
                "extractos": [recortar_texto(texto_p)],
            })

    patron_autoria = re.compile(
        r"(particip[oó]|coordin[oó]|dirigi[oó]|orden[oó]|autoriz[oó]|"
        r"ten[ií]a dominio del hecho|responsable del hecho)",
        flags=re.IGNORECASE,
    )

    for p in parrafos:
        texto_p = p["texto"]
        if patron_testimonio.search(texto_p) and patron_autoria.search(texto_p):
            resultados.append({
                "tipo": "Salto testimonial → autoría/responsabilidad",
                "parrafos": [p["n"]],
                "detalle": (
                    "Una declaración testimonial se utiliza para afirmar participación o autoría "
                    "sin puente indiciario objetivo."
                ),
                "extractos": [recortar_texto(texto_p)],
            })

    if len(parrafos_con_indicio) == 1:
        unico = parrafos_con_indicio[0]
        if unico["fuente_debil"] and patron_fuerza_indebida.search(unico["texto"]):
            resultados.append(
                {
                    "tipo": "Indicio único testimonial tratado como prueba fuerte",
                    "parrafos": [unico["n"]],
                    "detalle": (
                        "El único indicio, de fuente testimonial, es tratado como prueba contundente."
                    ),
                    "extractos": [recortar_texto(unico["texto"])],
                }
            )

    # ============================================================
    #  REGLA 6 – Cadena inferencial incompleta
    # ============================================================

    patron_conclusion = re.compile(
        r"(por tanto|por ende|en consecuencia|por consiguiente|"
        r"se concluye que|queda acreditado que|resulta acreditado que|"
        r"resulta probado que|se tiene por probado que)",
        flags=re.IGNORECASE,
    )

    patron_sustento = re.compile(
        r"(prueba|pruebas|indicio|indicios|hecho indiciario|hechos indiciarios|"
        r"pericia|perito|acta|informe|testigo|declaraci[oó]n|documento)",
        flags=re.IGNORECASE,
    )

    patron_causalidad = re.compile(
        r"(lo cual demuestra que|esto demuestra que|ello demuestra que|"
        r"lo que prueba que|esto evidencia que|ello evidencia que|"
        r"lo que acredita que)",
        flags=re.IGNORECASE,
    )

    for p in parrafos:
        texto_p = p["texto"]
        if patron_conclusion.search(texto_p) and not patron_sustento.search(texto_p):
            resultados.append({
                "tipo": "Conclusión sin sustento indiciario previo",
                "parrafos": [p["n"]],
                "detalle": (
                    "Se formula una conclusión fuerte sin integrar pruebas o indicios en el propio razonamiento."
                ),
                "extractos": [recortar_texto(texto_p)],
            })

        if patron_causalidad.search(texto_p) and not patron_sustento.search(texto_p):
            resultados.append(
                {
                    "tipo": "Afirmación causal sin explicación del vínculo (salto lógico)",
                    "parrafos": [p["n"]],
                    "detalle": (
                        "Se afirma que algo 'demuestra' o 'evidencia' un hecho sin explicitar "
                        "el vínculo entre los hechos y la conclusión."
                    ),
                    "extractos": [recortar_texto(texto_p)],
                }
            )

    patron_autoria_coord = re.compile(
        r"(coordin[oó]|dirigi[oó]|organiz[oó]|autoriz[oó]|"
        r"dispuso|control[oó]|ten[ií]a dominio del hecho)",
        flags=re.IGNORECASE,
    )

    patron_conocimiento = re.compile(
        r"(sab[ií]a que|ten[ií]a conocimiento de|no pod[ií]a ignorar|"
        r"deb[ií]a conocer|pleno conocimiento de)",
        flags=re.IGNORECASE,
    )

    for p in parrafos:
        texto_p = p["texto"]
        if patron_autoria_coord.search(texto_p) and not patron_sustento.search(texto_p):
            resultados.append(
                {
                    "tipo": "Afirmación de coordinación/autoría sin sustento indiciario",
                    "parrafos": [p["n"]],
                    "detalle": (
                        "Se afirma coordinación, dirección u organización sin integrar indicios concretos."
                    ),
                    "extractos": [recortar_texto(texto_p)],
                }
            )

        if patron_conocimiento.search(texto_p) and not patron_sustento.search(texto_p):
            resultados.append(
                {
                    "tipo": "Afirmación de conocimiento sin sustento probatorio",
                    "parrafos": [p["n"]],
                    "detalle": (
                        "Se afirma que el imputado 'sabía' o 'debía conocer' sin identificar el indicio que lo acredita."
                    ),
                    "extractos": [recortar_texto(texto_p)],
                }
            )

    # ============================================================
    #  REGLA 7 – Valoración contraria al contenido expreso de la prueba
    # ============================================================

    patron_medio_probatorio = re.compile(
        r"(declaraci[oó]n de|declar[oó] que|manifiest[oó] que|seg[uú]n el acta|"
        r"seg[uú]n consta en el acta|acta policial|acta fiscal|informe pericial|"
        r"informe t[eé]cnico|pericia oficial|pericia practicada|seg[uú]n el informe)",
        flags=re.IGNORECASE,
    )

    patron_contenido_negativo = re.compile(
        r"(no recuerda|no reconoci[oó]|no vio|no observ[oó]|no estuvo presente|"
        r"no le consta|no puede precisar|no puede afirmar|no se aprecia|"
        r"no se advierte|no se demuestra|no se acredita)",
        flags=re.IGNORECASE,
    )

    patron_conclusion_fuerte_prueba = re.compile(
        r"(de lo que se desprende que|de ello se desprende que|lo que demuestra que|"
        r"lo que acredita que|ello demuestra que|ello acredita que|"
        r"permite tener por acreditado que|confirma que|"
        r"demuestra claramente que|acredita de manera concluyente que)",
        flags=re.IGNORECASE,
    )

    for p in parrafos:
        texto_p = p["texto"]
        if (
            patron_medio_probatorio.search(texto_p)
            and patron_contenido_negativo.search(texto_p)
            and patron_conclusion_fuerte_prueba.search(texto_p)
        ):
            resultados.append(
                {
                    "tipo": "Valoración contraria al contenido expreso del medio probatorio (mismo párrafo)",
                    "parrafos": [p["n"]],
                    "detalle": (
                        "Se presenta un medio probatorio como demostrativo cuando el propio texto "
                        "reconoce que su contenido es negativo o dubitativo."
                    ),
                    "extractos": [recortar_texto(texto_p)],
                }
            )

    # ============================================================
    #  REGLA 8 – Hipótesis alternativas mal tratadas
    # ============================================================

    patron_alt_existencia = re.compile(
        r"(otras versiones|otras explicaciones|otras hipótesis|"
        r"hip[oó]tesis alternativa|versi[oó]n alternativa|"
        r"coartada|explicaci[oó]n del imputado|"
        r"otra posible explicaci[oó]n)",
        flags=re.IGNORECASE,
    )

    patron_no_descarta_alt2 = re.compile(
        r"(no se descartan|no puede descartarse|no puede excluirse|"
        r"no se ha descartado|no excluye la versi[oó]n del imputado)",
        flags=re.IGNORECASE,
    )

    patron_unica_conclusion = re.compile(
        r"(única explicaci[oó]n posible|única explicaci[oó]n razonable|"
        r"única conclusi[oó]n posible|única hip[oó]tesis plausible|"
        r"único camino l[oó]gico|conclusi[oó]n inevitable)",
        flags=re.IGNORECASE,
    )

    patron_descartar_sin_exp = re.compile(
        r"(no es cre[ií]ble|no resulta razonable|no convence al juzgador|"
        r"no es atendible|resulta inveros[ií]mil|no tiene asidero)",
        flags=re.IGNORECASE,
    )

    patron_analisis_alt = re.compile(
        r"(analiza la versi[oó]n alternativa|contrasta la hip[oó]tesis|"
        r"examina la explicaci[oó]n del imputado|"
        r"eval[uú]a la versi[oó]n alternativa)",
        flags=re.IGNORECASE,
    )

    for p in parrafos:
        texto_p = p["texto"]
        if patron_alt_existencia.search(texto_p) and patron_unica_conclusion.search(texto_p):
            resultados.append(
                {
                    "tipo": "Incongruencia: reconoce alternativas pero afirma única explicación",
                    "parrafos": [p["n"]],
                    "detalle": (
                        "Se reconocen hipótesis alternativas pero se mantiene una 'única explicación' como definitiva."
                    ),
                    "extractos": [recortar_texto(texto_p)],
                }
            )

        if patron_no_descarta_alt2.search(texto_p) and patron_unica_conclusion.search(texto_p):
            resultados.append(
                {
                    "tipo": "No se descartan alternativas pero se afirma conclusión única",
                    "parrafos": [p["n"]],
                    "detalle": (
                        "Se admite que no se descartan otras hipótesis y aun así se afirma una única conclusión."
                    ),
                    "extractos": [recortar_texto(texto_p)],
                }
            )

        if patron_alt_existencia.search(texto_p) and not patron_analisis_alt.search(texto_p):
            resultados.append(
                {
                    "tipo": "Mención de hipótesis alternativas sin análisis",
                    "parrafos": [p["n"]],
                    "detalle": (
                        "Se mencionan explicaciones alternativas sin analizarlas ni contrastarlas."
                    ),
                    "extractos": [recortar_texto(texto_p)],
                }
            )

        if patron_alt_existencia.search(texto_p) and patron_descartar_sin_exp.search(texto_p):
            resultados.append(
                {
                    "tipo": "Descarte injustificado de hipótesis alternativa",
                    "parrafos": [p["n"]],
                    "detalle": (
                        "Se descarta una versión alternativa con fórmulas vacías ('no es creíble', etc.) "
                        "sin justificación probatoria."
                    ),
                    "extractos": [recortar_texto(texto_p)],
                }
            )

        if patron_unica_conclusion.search(texto_p) and not patron_alt_existencia.search(texto_p):
            resultados.append(
                {
                    "tipo": "Conclusión única sin contrastar hipótesis alternativas",
                    "parrafos": [p["n"]],
                    "detalle": (
                        "Se sostiene una 'única explicación' sin referencia a posibles hipótesis alternativas."
                    ),
                    "extractos": [recortar_texto(texto_p)],
                }
            )

    # ============================================================
    #  REGLA 9 – Máximas de experiencia y sana crítica mal aplicadas
    # ============================================================

    patron_max_exp = re.compile(
        r"(m[aá]ximas de la experiencia|reglas de experiencia|"
        r"reglas de la experiencia com[uú]n|m[aá]ximas de experiencia com[uú]n)",
        flags=re.IGNORECASE,
    )

    patron_sana_critica = re.compile(
        r"(sana cr[ií]tica|reglas de la sana cr[ií]tica|"
        r"principios de la sana cr[ií]tica)",
        flags=re.IGNORECASE,
    )

    patron_generalizacion = re.compile(
        r"(lo normal es que|lo habitual es que|"
        r"es de experiencia com[uú]n que|"
        r"es de conocimiento general que|"
        r"suele ocurrir que|es l[oó]gico pensar que|"
        r"es natural que)",
        flags=re.IGNORECASE,
    )

    patron_estereotipo = re.compile(
        r"(quien nada debe nada teme|nadie inocente huye|"
        r"quien huye es porque algo teme|"
        r"todo narcotraficante|todo delincuente|"
        r"ninguna persona honesta|ning[uú]n inocente)",
        flags=re.IGNORECASE,
    )

    patron_sustento_exp = re.compile(
        r"(prueba|pruebas|indicio|indicios|hecho indiciario|hechos indiciarios|"
        r"pericia|perito|informe pericial|informe t[eé]cnico|"
        r"estudio estad[ií]stico|estad[ií]sticas|datos emp[ií]ricos|"
        r"acta|actas|documento|documentaci[oó]n)",
        flags=re.IGNORECASE,
    )

    for p in parrafos:
        texto_p = p["texto"]
        if (patron_max_exp.search(texto_p) or patron_sana_critica.search(texto_p)) and not patron_sustento_exp.search(texto_p):
            resultados.append(
                {
                    "tipo": "Invocación abstracta de máximas de experiencia/sana crítica sin explicación",
                    "parrafos": [p["n"]],
                    "detalle": (
                        "Se invocan genéricamente máximas de experiencia o sana crítica sin explicarlas "
                        "ni vincularlas con datos empíricos ni pruebas."
                    ),
                    "extractos": [recortar_texto(texto_p)],
                }
            )

        if patron_generalizacion.search(texto_p) and not patron_sustento_exp.search(texto_p):
            resultados.append(
                {
                    "tipo": "Generalización empírica sin sustento probatorio",
                    "parrafos": [p["n"]],
                    "detalle": (
                        "Se usan fórmulas como 'lo normal es que', 'es de experiencia común que', "
                        "sin apoyo en datos empíricos o pruebas específicas."
                    ),
                    "extractos": [recortar_texto(texto_p)],
                }
            )

        if patron_estereotipo.search(texto_p):
            resultados.append(
                {
                    "tipo": "Uso de máximas de experiencia estereotipadas/prejuiciosas",
                    "parrafos": [p["n"]],
                    "detalle": (
                        "Se utilizan estereotipos ('quien nada debe nada teme', etc.) como si fueran "
                        "verdaderas máximas de experiencia."
                    ),
                    "extractos": [recortar_texto(texto_p)],
                }
            )

    return resultados


# -------------------
# 5. Función principal
# -------------------

def analizar_incongruencias(texto: str) -> List[Dict[str, Any]]:
    if not texto or not texto.strip():
        return []
    parrafos = segmentar_parrafos(texto)
    parrafos_etq = etiquetar_parrafos(parrafos)
    return detectar_incongruencias(parrafos_etq)
