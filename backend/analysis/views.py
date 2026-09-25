import tempfile
from collections import defaultdict

from django.db.models import Count
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, parser_classes
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .loader import load_from_path
from .models import RiskResult, Student
from .scoring import DIMENSIONS, ITEMS, RISK_THRESHOLDS
from .serializers import (
    StudentDetailSerializer,
    StudentListSerializer,
)


class StudentViewSet(viewsets.ReadOnlyModelViewSet):
    """Lista y detalle de estudiantes con su resultado de riesgo."""
    queryset = Student.objects.select_related("result").all()
    filterset_fields = ["program", "semester", "sex", "result__level"]
    search_fields = ["full_name", "program"]
    ordering_fields = ["full_name", "result__total_pct", "age"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return StudentDetailSerializer
        return StudentListSerializer


class SummaryView(APIView):
    """Agregados globales para dashboards."""

    def get(self, request):
        results = RiskResult.objects.select_related("student").all()
        total = results.count()

        by_level = {"bajo": 0, "medio": 0, "alto": 0}
        for r in results.values("level").annotate(n=Count("id")):
            by_level[r["level"]] = r["n"]

        # promedio por dimensión (en %)
        dim_acc = defaultdict(lambda: {"sum": 0.0, "n": 0})
        for r in results:
            for d in r.dimensions:
                dim_acc[d["dimension"]]["sum"] += d["pct"]
                dim_acc[d["dimension"]]["n"] += 1
        dimensions = [
            {
                "dimension": d,
                "avg_pct": round(dim_acc[d]["sum"] / dim_acc[d]["n"], 4) if dim_acc[d]["n"] else 0.0,
            }
            for d in DIMENSIONS
        ]

        # distribución por programa y semestre (conteo por nivel)
        def group_by(field):
            out = defaultdict(lambda: {"bajo": 0, "medio": 0, "alto": 0, "total": 0})
            qs = Student.objects.select_related("result").all()
            for s in qs:
                key = getattr(s, field) or "(sin dato)"
                lvl = s.result.level if hasattr(s, "result") else None
                if lvl:
                    out[key][lvl] += 1
                    out[key]["total"] += 1
            return [{"key": k, **v} for k, v in sorted(out.items())]

        alerts_students = results.exclude(alerts=[]).count()

        return Response({
            "total_students": total,
            "by_level": by_level,
            "dimensions": dimensions,
            "by_program": group_by("program"),
            "by_semester": group_by("semester"),
            "by_sex": group_by("sex"),
            "students_with_alerts": alerts_students,
        })


class AlertsView(APIView):
    """Estudiantes con alertas de ítems críticos."""

    def get(self, request):
        out = []
        for r in RiskResult.objects.select_related("student").exclude(alerts=[]):
            out.append({
                "id": r.student.id,
                "full_name": r.student.full_name,
                "program": r.student.program,
                "semester": r.student.semester,
                "level": r.level,
                "alerts": r.alerts,
            })
        out.sort(key=lambda x: len(x["alerts"]), reverse=True)
        return Response(out)


class BaremoView(APIView):
    """Expone la configuración del baremo (para transparencia / UI)."""

    def get(self, request):
        return Response({
            "dimensions": DIMENSIONS,
            "thresholds": [
                {"level": n, "min_pct": lo, "max_pct": min(hi, 1.0)}
                for n, lo, hi in RISK_THRESHOLDS
            ],
            "items": [
                {"label": it["label"], "dimension": it["dimension"],
                 "alarm_at": it.get("alarm")}
                for it in ITEMS
            ],
        })


@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
def upload_excel(request):
    """Sube un .xlsx del formulario y recalcula resultados."""
    f = request.FILES.get("file")
    if not f:
        return Response({"detail": "Falta el archivo 'file'."},
                        status=status.HTTP_400_BAD_REQUEST)
    sheet = request.data.get("sheet")
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=True) as tmp:
        for chunk in f.chunks():
            tmp.write(chunk)
        tmp.flush()
        try:
            stats = load_from_path(tmp.name, sheet)
        except Exception as exc:  # noqa: BLE001
            return Response({"detail": f"Error al procesar: {exc}"},
                            status=status.HTTP_400_BAD_REQUEST)
    return Response(stats, status=status.HTTP_201_CREATED)
