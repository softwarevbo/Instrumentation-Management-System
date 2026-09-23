from django.urls import path
from . import views

app_name = 'telescopes'

urlpatterns = [
    path('', views.telescope_list_view, name='telescope_list'),
    path('discussions/', views.discussion_hub_view, name='discussion_hub'),
    path('discussions/create/', views.discussion_create_view, name='discussion_create'),
    path('discussions/<int:pk>/', views.discussion_detail_view, name='discussion_detail'),
    path('discussions/<int:pk>/pin/', views.toggle_pin_discussion_view, name='toggle_pin_discussion'),
    path('create/', views.telescope_create_view, name='telescope_create'),
    path('<int:pk>/', views.telescope_detail_view, name='telescope_detail'),
    path('<int:pk>/edit/', views.telescope_edit_view, name='telescope_edit'),
    path('<int:pk>/slew/', views.slew_telescope_view, name='telescope_slew'),
    path('<int:pk>/stop/', views.stop_telescope_view, name='stop_telescope'),
    path('<int:pk>/toggle-dome/', views.toggle_dome_view, name='toggle_dome'),
    path('<int:pk>/update-telemetry/', views.update_telemetry_view, name='update_telemetry'),
]


