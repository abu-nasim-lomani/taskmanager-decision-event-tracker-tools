# events/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('new/', views.event_create, name='event_create'), 
]