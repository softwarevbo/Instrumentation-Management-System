from django.urls import path
from . import views

app_name = 'platesolver'

urlpatterns = [
    path('', views.index_view, name='index'),
    path('api/field/', views.api_get_field_view, name='api_get_field'),
    path('api/solve/', views.api_solve_field_view, name='api_solve_field'),
    path('api/sync/', views.api_sync_telescope_view, name='api_sync_telescope'),
]
