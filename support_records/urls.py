from django.urls import path
from . import views

app_name = 'support_records'

urlpatterns = [
    path('', views.support_record_list, name='list'),
    path('<int:pk>/', views.support_record_detail, name='detail'),
    path('create/', views.support_record_create, name='create'),
    path('<int:pk>/update/', views.support_record_update, name='update'),
    path('<int:pk>/delete/', views.support_record_delete, name='delete'),
]
