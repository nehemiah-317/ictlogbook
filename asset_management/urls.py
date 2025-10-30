from django.urls import path
from . import views

app_name = 'asset_management'

urlpatterns = [
    path('', views.asset_record_list, name='list'),
    path('<int:pk>/', views.asset_record_detail, name='detail'),
    path('create/', views.asset_record_create, name='create'),
    path('<int:pk>/update/', views.asset_record_update, name='update'),
    path('<int:pk>/delete/', views.asset_record_delete, name='delete'),
]
