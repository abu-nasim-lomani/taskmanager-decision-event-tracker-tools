# events/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('my-events/', views.my_events, name='my_events'),
    path('new/', views.event_create, name='event_create'),
    path('<int:pk>/', views.event_detail, name='event_detail'),
    path('<int:pk>/edit/', views.event_update, name='event_update'), 
    path('<int:pk>/delete/', views.event_delete, name='event_delete'),
    path('invitation/<int:invitation_pk>/respond/<str:response>/', views.respond_to_invitation, name='respond_to_invitation'),
    path('my-events/json/', views.my_events_json, name='my_events_json'),
]