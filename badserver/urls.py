from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", include("parking.urls")),
    path("api/", include("parking.api.urls")),
    path("admin/", admin.site.urls),
]
