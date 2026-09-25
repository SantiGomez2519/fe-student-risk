from django.db import models


class Student(models.Model):
    """Un estudiante y su caracterización (una fila del formulario)."""
    full_name = models.CharField(max_length=200, db_index=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    sex = models.CharField(max_length=30, blank=True)
    program = models.CharField(max_length=120, blank=True, db_index=True)
    semester = models.CharField(max_length=20, blank=True)
    city_origin = models.CharField(max_length=120, blank=True)
    city_current = models.CharField(max_length=120, blank=True)
    lives_with = models.CharField(max_length=120, blank=True)
    first_generation = models.CharField(max_length=60, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)

    # payload crudo de la fila (por si se necesita re-puntuar)
    raw = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["full_name"]

    def __str__(self):
        return self.full_name


class RiskResult(models.Model):
    """Resultado de puntuación asociado a un estudiante."""
    LEVELS = [("bajo", "Bajo"), ("medio", "Medio"), ("alto", "Alto")]

    student = models.OneToOneField(
        Student, on_delete=models.CASCADE, related_name="result"
    )
    total = models.IntegerField(default=0)
    total_max = models.IntegerField(default=0)
    total_pct = models.FloatField(default=0.0)
    level = models.CharField(max_length=10, choices=LEVELS, default="bajo", db_index=True)

    # detalle por dimensión, ítems y alertas (tal como los produce scoring.py)
    dimensions = models.JSONField(default=list, blank=True)
    items = models.JSONField(default=list, blank=True)
    alerts = models.JSONField(default=list, blank=True)

    computed_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student.full_name} · {self.level} ({self.total_pct:.0%})"

    @property
    def has_alerts(self) -> bool:
        return bool(self.alerts)
