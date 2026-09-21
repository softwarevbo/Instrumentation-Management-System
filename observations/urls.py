from django.urls import path
from . import views

app_name = 'observations'

urlpatterns = [
    path('targets/', views.target_list_view, name='target_list'),
    path('targets/create/', views.target_create_view, name='target_create'),
    path('targets/<int:pk>/edit/', views.target_edit_view, name='target_edit'),
    path('targets/<int:pk>/delete/', views.target_delete_view, name='target_delete'),
]
