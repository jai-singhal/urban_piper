from django.contrib import admin
from django.urls import path, include
from urban_piper.core import views

urlpatterns = [
    path('', views.index, name="index"),
    path('dp/', views.DeliveryPersonView.as_view(), name="delivery_person"),
    path('sm/', views.StorageManagerView.as_view(), name="storage_manager"),

]
