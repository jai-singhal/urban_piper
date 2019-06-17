from django.conf.urls import url

from avyukt.core import consumers

websocket_urlpatterns = [
    url(r'^ws/task/$', consumers.DeliveryTaskConsumer),
]
