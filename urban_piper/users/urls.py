
from django.contrib import admin
from django.urls import path, include
from urban_piper.users import views

urlpatterns = [
    path('login/', views.login_view, name="login"),
    path('logout/', views.logout_view, name="logout"),
]
