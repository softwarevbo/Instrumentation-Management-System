from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('feedback/', views.feedback_view, name='feedback'),
    path('feedback/<int:pk>/respond/', views.feedback_respond_view, name='feedback_respond'),
    path('notifications/read/', views.mark_notifications_read, name='mark_notifications_read'),
]


