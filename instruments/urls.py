from django.urls import path
from . import views

app_name = 'instruments'

urlpatterns = [
    path('', views.instrument_list_view, name='instrument_list'),
    path('create/', views.instrument_create_view, name='instrument_create'),
    path('<int:pk>/', views.instrument_detail_view, name='instrument_detail'),
    path('<int:pk>/edit/', views.instrument_edit_view, name='instrument_edit'),
    path('<int:pk>/status/', views.update_status_view, name='update_status'),
]
