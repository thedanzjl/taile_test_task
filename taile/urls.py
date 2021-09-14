from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from drf_yasg.generators import OpenAPISchemaGenerator

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls'))
]

schema_view = get_schema_view(
    openapi.Info(
        title="REST API",
        description="# REST API тестовой задачи",
        default_version="v1"
    ),
    public=False,
    generator_class=OpenAPISchemaGenerator,
    patterns=urlpatterns
)

urlpatterns += [
    path(
        "swagger/<format>/",
        schema_view.without_ui(cache_timeout=0),
        name="swagger-yaml",
    ),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger"),
]
