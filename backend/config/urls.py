from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from analysis.views import (
    AlertsView,
    BaremoView,
    StudentViewSet,
    SummaryView,
    upload_excel,
)

router = DefaultRouter()
router.register(r"students", StudentViewSet, basename="student")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api/summary/", SummaryView.as_view(), name="summary"),
    path("api/alerts/", AlertsView.as_view(), name="alerts"),
    path("api/baremo/", BaremoView.as_view(), name="baremo"),
    path("api/upload/", upload_excel, name="upload"),
]
