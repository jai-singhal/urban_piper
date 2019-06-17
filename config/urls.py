from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('django-rq/', include('django_rq.urls')),

    path('', include(("avyukt.core.urls", "core"), namespace="core")),
    path('accounts/', include(("avyukt.users.urls", "core"), namespace="users")),

]
