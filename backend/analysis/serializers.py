from rest_framework import serializers

from .models import RiskResult, Student


class RiskResultSerializer(serializers.ModelSerializer):
    has_alerts = serializers.BooleanField(read_only=True)

    class Meta:
        model = RiskResult
        fields = [
            "total", "total_max", "total_pct", "level",
            "dimensions", "items", "alerts", "has_alerts", "computed_at",
        ]


class StudentListSerializer(serializers.ModelSerializer):
    """Versión ligera para listados/tabla con semáforo de riesgo."""
    level = serializers.CharField(source="result.level", read_only=True, default=None)
    total_pct = serializers.FloatField(source="result.total_pct", read_only=True, default=None)
    alerts_count = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = [
            "id", "full_name", "age", "sex", "program", "semester",
            "level", "total_pct", "alerts_count",
        ]

    def get_alerts_count(self, obj):
        result = getattr(obj, "result", None)
        return len(result.alerts) if result else 0


class StudentDetailSerializer(serializers.ModelSerializer):
    result = RiskResultSerializer(read_only=True)

    class Meta:
        model = Student
        fields = [
            "id", "full_name", "age", "sex", "program", "semester",
            "city_origin", "city_current", "lives_with", "first_generation",
            "submitted_at", "raw", "result",
        ]
