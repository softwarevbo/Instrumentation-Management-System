from django.urls import path
from . import views

app_name = 'telescopes'

urlpatterns = [
    path('', views.telescope_list_view, name='telescope_list'),
    path('create/', views.telescope_create_view, name='telescope_create'),
    path('<int:pk>/', views.telescope_detail_view, name='telescope_detail'),
    path('<int:pk>/edit/', views.telescope_edit_view, name='telescope_edit'),
    path('<int:pk>/slew/', views.slew_telescope_view, name='telescope_slew'),
    path('<int:pk>/toggle-dome/', views.toggle_dome_view, name='toggle_dome'),
    path('<int:pk>/update-telemetry/', views.update_telemetry_view, name='update_telemetry'),
]

