"""
Motor de puntuación (baremo) del análisis de riesgo estudiantil.

Diseño:
- Cada ítem del cuestionario pertenece a una DIMENSIÓN.
- Cada ítem tiene una ESCALA (mapa de texto de respuesta -> valor 0..4).
- La DIRECCIÓN ya viene reflejada dentro del propio mapa de la escala
  (p. ej. en un ítem "inverso" 'Totalmente de acuerdo' vale 0 y
  'Totalmente en desacuerdo' vale 4), tal como está codificado en el
  instrumento original.
- Algunos ítems son de ALARMA: si superan un umbral individual, generan
  una alerta roja para ese estudiante sin importar el puntaje global.
- El nivel de riesgo (bajo/medio/alto) se calcula por porcentaje del máximo
  posible, con cortes configurables (RISK_THRESHOLDS).

Todo aquí es CONFIGURABLE: para cambiar el baremo basta con editar este
archivo (o, más adelante, moverlo a la base de datos / panel de admin).
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Escalas reutilizables: texto de respuesta -> valor (0..4)
# ---------------------------------------------------------------------------

# Frecuencia estándar de 5 niveles (normal: más frecuencia = más riesgo)
FREQ5 = {
    "Nunca": 0,
    "Rara vez": 1,
    "Algunas veces": 2,
    "Frecuentemente": 3,
    "Siempre": 4,
}

# Frecuencia de 4 niveles tipo PHQ (con "salto" a 4 en el nivel máximo)
FREQ4_SALTO = {
    "Nunca": 0,
    "Varios días": 1,
    "Más de la mitad de los días": 2,
    "Más de la mitad": 2,
    "Casi todos los días": 4,
}

# Acuerdo directo (más de acuerdo = más riesgo)
ACUERDO_DIRECTO = {
    "Totalmente en desacuerdo": 0,
    "En desacuerdo": 1,
    "Ni de acuerdo ni en desacuerdo": 2,
    "De acuerdo": 3,
    "Totalmente de acuerdo": 4,
}

# Acuerdo inverso (más de acuerdo = MENOS riesgo)
ACUERDO_INVERSO = {
    "Totalmente de acuerdo": 0,
    "De acuerdo": 1,
    "Ni de acuerdo ni en desacuerdo": 2,
    "En desacuerdo": 3,
    "Totalmente en desacuerdo": 4,
}

# Frecuencia inversa (más frecuencia = MENOS riesgo)
FREQ5_INV = {
    "Siempre": 0,
    "Frecuentemente": 1,
    "Algunas veces": 2,
    "Rara vez": 3,
    "Nunca": 4,
}

# Intensidad (Nada..Extremadamente)
INTENSIDAD = {
    "Nada": 0,
    "Poco": 1,
    "Moderadamente": 2,
    "Mucho": 3,
    "Extremadamente": 4,
}

# Dificultad (Ninguna..Extrema)
DIFICULTAD = {
    "Ninguna": 0,
    "Poca": 1,
    "Moderada": 2,
    "Mucha": 3,
    "Extrema": 4,
}

# Sí/No con Sí = riesgo alto
SINO_SI_RIESGO = {"No": 0, "Sí": 4, "Si": 4}
# Sí/No con No = riesgo (p. ej. "cuenta con computador propio")
SINO_NO_RIESGO = {"Sí": 0, "Si": 0, "No": 4}

# Probabilidad de deserción
PROBABILIDAD = {
    "Nada probable": 0,
    "Poco probable": 1,
    "Moderadamente probable": 2,
    "Probable": 3,
    "Muy probable": 4,
}

# Desempeño académico autopercibido (Muy malo = mayor riesgo)
DESEMPENO = {
    "Muy bueno": 0,
    "Bueno": 1,
    "Regular": 2,
    "Malo": 3,
    "Muy malo": 4,
}

# Horas de estudio independiente (muy pocas = riesgo)
HORAS_ESTUDIO = {
    "Más de 15": 0,
    "10-15": 0,
    "6-9": 1,
    "3-5": 3,
    "0-2": 4,
    "Menos de 3": 4,
}


def _val_asignaturas_perdidas(raw) -> int:
    """0 materias = 0, 1 = 2, 2 = 3, 3+ = 4."""
    try:
        n = int(float(raw))
    except (TypeError, ValueError):
        return 0
    if n <= 0:
        return 0
    if n == 1:
        return 2
    if n == 2:
        return 3
    return 4


# ---------------------------------------------------------------------------
# Definición de ítems.
# key      -> columna del formulario (encabezado exacto) o id lógico
# label    -> texto legible corto
# dimension-> dimensión a la que aporta
# scale    -> dict de mapeo, o "custom" para funciones especiales
# alarm    -> valor a partir del cual dispara alerta individual (o None)
# ---------------------------------------------------------------------------

ITEMS = [
    # ---------------- Bloque Académico ----------------
    {"key": "¿Cómo considera su desempeño académico durante el último semestre?",
     "label": "Desempeño académico", "dimension": "Académico", "scale": DESEMPENO},
    {"key": "¿Cuántas asignaturas perdió el semestre anterior?",
     "label": "Asignaturas perdidas", "dimension": "Académico", "scale": "asignaturas"},
    {"key": "¿Con qué frecuencia entrega actividades fuera del plazo establecido?",
     "label": "Entregas tardías", "dimension": "Académico", "scale": FREQ5},
    {"key": "En una semana normal, ¿cuántas horas dedica al estudio independiente?",
     "label": "Horas de estudio", "dimension": "Académico", "scale": HORAS_ESTUDIO},
    {"key": "¿Con qué frecuencia deja las actividades académicas para el último momento?",
     "label": "Procrastinación", "dimension": "Académico", "scale": FREQ5},
    {"key": "Cuando no entiende un tema busca ayuda oportunamente.",
     "label": "Busca ayuda", "dimension": "Académico", "scale": FREQ5_INV},
    {"key": "Tiene un horario organizado para estudiar.",
     "label": "Organización", "dimension": "Académico", "scale": ACUERDO_INVERSO},
    {"key": "Siente que la carga académica supera su capacidad para responder adecuadamente.",
     "label": "Sobrecarga académica", "dimension": "Académico", "scale": ACUERDO_DIRECTO},
    {"key": "Se siente preparado para comprender los contenidos de las asignaturas.",
     "label": "Preparación percibida", "dimension": "Académico", "scale": ACUERDO_INVERSO},
    {"key": "Tiene dificultades para redactar trabajos académicos.",
     "label": "Dificultad redacción", "dimension": "Académico", "scale": DIFICULTAD},
    {"key": "Tiene dificultades para comprender textos académicos complejos.",
     "label": "Dificultad comprensión", "dimension": "Académico", "scale": DIFICULTAD},
    {"key": "Tiene dificultades en matemáticas básicas necesarias para su carrera.",
     "label": "Dificultad matemáticas", "dimension": "Académico", "scale": DIFICULTAD},

    # ---------------- Bloque Recursos / Digital ----------------
    {"key": "Cuenta con computador propio para estudiar.",
     "label": "Computador propio", "dimension": "Recursos", "scale": SINO_NO_RIESGO},
    {"key": "Su conexión a internet es suficiente para cumplir sus actividades académicas.",
     "label": "Conexión a internet", "dimension": "Recursos", "scale": ACUERDO_INVERSO},
    {"key": "Utiliza herramientas de Inteligencia Artificial para aprender de manera responsable.",
     "label": "Uso responsable de IA", "dimension": "Recursos", "scale": FREQ5_INV},
    {"key": "Sabe verificar la calidad de la información que encuentra en internet o mediante IA.",
     "label": "Verificación de información", "dimension": "Recursos", "scale": ACUERDO_INVERSO},
    {"key": "Pasa más tiempo del que quisiera en redes sociales.",
     "label": "Uso excesivo de redes", "dimension": "Recursos", "scale": FREQ5},

    # ---------------- Bloque Motivación / Deserción ----------------
    {"key": "Tiene claridad sobre su proyecto profesional.",
     "label": "Claridad de proyecto", "dimension": "Motivación", "scale": ACUERDO_INVERSO},
    {"key": "Actualmente ha pensado en abandonar sus estudios.",
     "label": "Ideación de abandono (actual)", "dimension": "Motivación",
     "scale": ACUERDO_DIRECTO, "alarm": 3},
    {"key": "Cuando algo sale mal busca nuevas estrategias para intentarlo nuevamente.",
     "label": "Resiliencia", "dimension": "Motivación", "scale": ACUERDO_INVERSO},
    {"key": "Considera que puede resolver problemas difíciles si se esfuerza.",
     "label": "Autoeficacia", "dimension": "Motivación", "scale": ACUERDO_INVERSO},
    {"key": "En general, se siente optimista respecto a su futuro académico.",
     "label": "Optimismo", "dimension": "Motivación", "scale": ACUERDO_INVERSO},
    {"key": "Durante el último semestre ha pensado en abandonar sus estudios.",
     "label": "Ideación de abandono (semestre)", "dimension": "Motivación",
     "scale": FREQ5, "alarm": 3},
    {"key": "¿Qué tan probable considera que es abandonar sus estudios durante el próximo año?",
     "label": "Probabilidad de deserción", "dimension": "Motivación",
     "scale": PROBABILIDAD, "alarm": 3},

    # ---------------- Bloque Económico ----------------
    {"key": "Los ingresos familiares alcanzan para cubrir los gastos básicos.",
     "label": "Ingresos suficientes", "dimension": "Económico", "scale": ACUERDO_INVERSO},
    {"key": "En algún momento del último mes ha dejado de comer por falta de dinero.",
     "label": "Inseguridad alimentaria", "dimension": "Económico",
     "scale": FREQ5, "alarm": 2},
    {"key": "Tiene dificultades para costear el transporte hacia la universidad.",
     "label": "Dificultad de transporte", "dimension": "Económico", "scale": DIFICULTAD},
    {"key": "Su vivienda ofrece un espacio adecuado para estudiar.",
     "label": "Vivienda adecuada", "dimension": "Económico", "scale": ACUERDO_INVERSO},
    {"key": "Durante el último año su familia enfrentó una crisis económica importante.",
     "label": "Crisis económica familiar", "dimension": "Económico", "scale": SINO_SI_RIESGO},
    {"key": "¿Actualmente tiene deudas personales que le generan preocupación?",
     "label": "Deudas preocupantes", "dimension": "Económico", "scale": SINO_SI_RIESGO},
    {"key": "Si surgiera un gasto inesperado equivalente a un salario mínimo, su hogar podría asumirlo.",
     "label": "Capacidad ante imprevistos", "dimension": "Económico", "scale": ACUERDO_INVERSO},
    {"key": "¿Ha pensado abandonar sus estudios por razones económicas?",
     "label": "Abandono por economía", "dimension": "Económico",
     "scale": FREQ5, "alarm": 2},
    {"key": "Percibe estrés constante por su situación financiera o la de su hogar.",
     "label": "Estrés financiero", "dimension": "Económico", "scale": INTENSIDAD},
]

# Dimensiones y su orden de presentación
DIMENSIONS = ["Académico", "Recursos", "Motivación", "Económico"]

# ---------------------------------------------------------------------------
# Baremo: cortes de nivel de riesgo por % del máximo posible.
# Se aplica tanto al total como a cada dimensión.
# ---------------------------------------------------------------------------
RISK_THRESHOLDS = [
    ("bajo", 0.0, 0.25),     # 0% - 25%
    ("medio", 0.25, 0.50),   # 25% - 50%
    ("alto", 0.50, 1.01),    # 50% - 100%
]


def value_for(item: dict, raw):
    """Devuelve el valor 0..4 de una respuesta cruda según la escala del ítem."""
    if raw is None:
        return None
    scale = item["scale"]
    if scale == "asignaturas":
        return _val_asignaturas_perdidas(raw)
    key = str(raw).strip()
    return scale.get(key)


def risk_level(pct: float) -> str:
    for name, lo, hi in RISK_THRESHOLDS:
        if lo <= pct < hi:
            return name
    return "alto"


def score_response(row: dict) -> dict:
    """
    row: dict {encabezado_columna: valor_crudo}
    Devuelve el análisis completo: por ítem, por dimensión, total y alertas.
    """
    per_item = []
    dim_score = {d: 0 for d in DIMENSIONS}
    dim_max = {d: 0 for d in DIMENSIONS}
    alerts = []

    for item in ITEMS:
        raw = row.get(item["key"])
        val = value_for(item, raw)
        answered = val is not None
        v = val if answered else 0
        dim = item["dimension"]
        dim_score[dim] += v
        if answered:
            dim_max[dim] += 4
        per_item.append({
            "key": item["key"],
            "label": item["label"],
            "dimension": dim,
            "raw": None if raw is None else str(raw).strip(),
            "value": val,
        })
        alarm = item.get("alarm")
        if alarm is not None and answered and v >= alarm:
            alerts.append({
                "label": item["label"],
                "dimension": dim,
                "value": v,
                "raw": str(raw).strip(),
            })

    dimensions = []
    total = 0
    total_max = 0
    for d in DIMENSIONS:
        s = dim_score[d]
        m = dim_max[d]
        pct = (s / m) if m else 0.0
        dimensions.append({
            "dimension": d,
            "score": s,
            "max": m,
            "pct": round(pct, 4),
            "level": risk_level(pct),
        })
        total += s
        total_max += m

    total_pct = (total / total_max) if total_max else 0.0
    return {
        "total": total,
        "total_max": total_max,
        "total_pct": round(total_pct, 4),
        "level": risk_level(total_pct),
        "dimensions": dimensions,
        "alerts": alerts,
        "items": per_item,
    }
