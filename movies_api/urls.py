from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="CODED_Movies API",
        default_version="v1",
        description="Films + Comments (SWAPI-backed)",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("admin/", admin.site.urls),
    # Swagger UI lives at /docs/
    path("docs/", schema_view.with_ui("swagger", cache_timeout=0), name="swagger-ui"),
    # DRF API root + routers live under /api/
    path("api/", include("films.urls")),
]

# Serve static files in development mode
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
