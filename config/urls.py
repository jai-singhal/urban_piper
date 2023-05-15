from django.contrib import admin
from django.urls import path, include
from django.conf import settings
import debug_toolbar

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('django-rq/', include('django_rq.urls')),

    path('', include(("avyukt.core.urls", "core"), namespace="core")),
    path('accounts/', include(("avyukt.users.urls", "core"), namespace="users")),
    
]
if settings.DEBUG:
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls)),]

