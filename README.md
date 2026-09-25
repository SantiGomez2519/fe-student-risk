# fe-student-risk

Aplicación web para el **análisis de riesgo estudiantil** a partir de las
respuestas del formulario de caracterización y bienestar. Calcula un puntaje
de riesgo por estudiante y por dimensión, clasifica el nivel (bajo / medio /
alto) según un **baremo configurable** y genera alertas para ítems críticos.

- **Backend:** Django + Django REST Framework (SQLite por defecto, listo para PostgreSQL).
- **Frontend:** Vue 3 + Vite + Pinia + Vue Router, gráficas con Chart.js.
- **Fuente de datos:** el Excel `Resultados — Riesgo Estudiantil.xlsx` (hoja `Form Responses 1`).

---

## Estructura

```
fe-student-risk/
├── backend/                 # Django + DRF
│   ├── analysis/
│   │   ├── scoring.py       # 👈 BAREMO: dimensiones, escalas, umbrales, alertas
│   │   ├── loader.py        # lectura del Excel + cálculo de resultados
│   │   ├── models.py        # Student, RiskResult
│   │   ├── views.py         # endpoints REST
│   │   └── management/commands/load_data.py
│   └── config/              # settings, urls
├── frontend/                # Vue 3 + Vite
│   └── src/
│       ├── views/           # Dashboard, Students, StudentDetail, Alerts, Upload
│       ├── components/
│       └── api.js
├── Instrumento Riesgo Psicosocial.xlsx     # instrumento (definición de ítems)
└── Resultados — Riesgo Estudiantil.xlsx    # datos del formulario (seed)
```

---

## Puesta en marcha

### 1) Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # opcional
pip install -r requirements.txt

python manage.py migrate
python manage.py load_data          # carga el Excel del repositorio
python manage.py runserver          # http://127.0.0.1:8000
```

Para usar otro archivo Excel:

```bash
python manage.py load_data "/ruta/a/otro.xlsx" --sheet "Form Responses 1"
```

### 2) Frontend

```bash
cd frontend
npm install
npm run dev                          # http://localhost:5173
```

El servidor de Vite hace *proxy* de `/api` hacia `http://127.0.0.1:8000`,
así que basta con tener el backend corriendo.

---

## API

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/students/` | Lista con nivel de riesgo (filtros: `program`, `semester`, `sex`, `result__level`; `search`, `ordering`) |
| GET | `/api/students/{id}/` | Ficha individual: dimensiones, ítems y alertas |
| GET | `/api/summary/` | Agregados para dashboard (por nivel, dimensión, programa, semestre, sexo) |
| GET | `/api/alerts/` | Estudiantes con ítems críticos |
| GET | `/api/baremo/` | Configuración del baremo (transparencia) |
| POST | `/api/upload/` | Sube un `.xlsx` (`multipart/form-data`, campo `file`) y recalcula |

---

## Baremo (cómo se puntúa)

Todo el modelo de puntuación vive en **`backend/analysis/scoring.py`** y es
fácil de ajustar.

- Cada ítem se mapea a un valor **0–4** según su escala (frecuencia, acuerdo
  directo/inverso, intensidad, dificultad, sí/no…). La **dirección** del ítem
  (normal vs. inversa) queda reflejada en el propio mapa.
- Los ítems se agrupan en **dimensiones**: `Académico`, `Recursos`,
  `Motivación`, `Económico`.
- El **nivel de riesgo** se calcula por el porcentaje del máximo posible, con
  cortes configurables (`RISK_THRESHOLDS`):

  | Nivel | Rango (% del máximo) |
  |-------|----------------------|
  | Bajo  | 0 % – 25 % |
  | Medio | 25 % – 50 % |
  | Alto  | ≥ 50 % |

- Algunos ítems son de **alarma** (p. ej. ideación de abandono, inseguridad
  alimentaria): si superan un umbral individual generan una alerta roja para
  ese estudiante, independientemente del puntaje global.

> El baremo por defecto fue propuesto por el equipo de desarrollo y **puede
> cambiarse en cualquier momento** editando `scoring.py` (o migrándolo a la
> base de datos / panel de administración más adelante). Tras cambiarlo,
> reejecutar `python manage.py load_data` para recalcular.

### Nota sobre los dos Excel

- `Resultados — Riesgo Estudiantil.xlsx` (hoja `Form Responses 1`) es la
  **fuente real de datos** (una fila por estudiante, incluye `Nombre Completo`).
- `Instrumento Riesgo Psicosocial.xlsx` describe el **instrumento psicosocial**
  (preguntas, dirección y puntaje por opción). Sus hojas por estudiante están
  aún sin diligenciar; cuando se llenen, se puede extender `scoring.py` para
  incorporar esa dimensión psicosocial adicional.

---

## PostgreSQL (opcional)

Define variables de entorno y el backend usará Postgres en vez de SQLite:

```bash
export POSTGRES_DB=riesgo POSTGRES_USER=... POSTGRES_PASSWORD=... \
       POSTGRES_HOST=localhost POSTGRES_PORT=5432
```
