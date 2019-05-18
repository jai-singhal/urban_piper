from django.conf.urls import url

from urban_piper.core import consumers

websocket_urlpatterns = [
    url(r'^ws/sm/$', consumers.StorageManagerConsumer),
    url(r'^ws/dp/$', consumers.DeliveryPersonConsumer),

]