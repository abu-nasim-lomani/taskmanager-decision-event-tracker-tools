# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.meeting_list, name='meeting_list'),
    path('meeting/<int:pk>/', views.meeting_detail, name='meeting_detail'),
]