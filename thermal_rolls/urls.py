from django.urls import path
from . import views

app_name = 'thermal_rolls'

urlpatterns = [
    path('', views.thermal_roll_list, name='list'),
    path('<int:pk>/', views.thermal_roll_detail, name='detail'),
    path('create/', views.thermal_roll_create, name='create'),
    path('<int:pk>/update/', views.thermal_roll_update, name='update'),
    path('<int:pk>/delete/', views.thermal_roll_delete, name='delete'),
]
