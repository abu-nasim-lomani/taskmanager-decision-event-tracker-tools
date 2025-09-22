# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.meeting_list, name='meeting_list'),
    path('meeting/new/', views.meeting_create, name='meeting_create'),
    path('meeting/<int:pk>/', views.meeting_detail, name='meeting_detail'),
    path('meeting/<int:pk>/edit/', views.meeting_update, name='meeting_update'),
    path('meeting/<int:pk>/delete/', views.meeting_delete, name='meeting_delete'), 
    path('task/<int:pk>/edit/', views.task_update, name='task_update'),
    path('task/<int:pk>/delete/', views.task_delete, name='task_delete'),
    path('my-tasks/', views.my_tasks, name='my_tasks'),
    path('management-dashboard/', views.management_dashboard, name='management_dashboard'),
]