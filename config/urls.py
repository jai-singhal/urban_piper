from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('django-rq/', include('django_rq.urls')),

    path('', include(("urban_piper.core.urls", "core"), namespace="core")),
    path('accounts/', include(("urban_piper.users.urls", "core"), namespace="users")),

]
