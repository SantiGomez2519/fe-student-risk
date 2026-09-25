from django.contrib import admin

from .models import RiskResult, Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("full_name", "program", "semester", "sex", "age")
    search_fields = ("full_name", "program")
    list_filter = ("program", "sex", "semester")


@admin.register(RiskResult)
class RiskResultAdmin(admin.ModelAdmin):
    list_display = ("student", "level", "total", "total_max", "total_pct")
    list_filter = ("level",)
    search_fields = ("student__full_name",)
