from django.urls import path
from . import views

app_name = 'maintenance'

urlpatterns = [
    path('tickets/', views.ticket_list_view, name='ticket_list'),
    path('tickets/create/', views.ticket_create_view, name='ticket_create'),
    path('tickets/<int:pk>/', views.ticket_detail_view, name='ticket_detail'),
    path('tickets/<int:pk>/resolve/', views.ticket_resolve_view, name='ticket_resolve'),
    path('calibrations/', views.calibration_list_view, name='calibration_list'),
    path('calibrations/create/', views.calibration_create_view, name='calibration_create'),
    path('calibrations/<int:pk>/status/', views.calibration_status_update_view, name='calibration_status_update'),
]

