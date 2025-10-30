from django.urls import path
from . import views

app_name = 'vendor_assistance'

urlpatterns = [
    path('', views.vendor_assistance_list, name='list'),
    path('<int:pk>/', views.vendor_assistance_detail, name='detail'),
    path('create/', views.vendor_assistance_create, name='create'),
    path('<int:pk>/update/', views.vendor_assistance_update, name='update'),
    path('<int:pk>/delete/', views.vendor_assistance_delete, name='delete'),
]
