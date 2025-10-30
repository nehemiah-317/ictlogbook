from django.urls import path, include
from django.contrib import admin
from accounts import views as accounts_views

urlpatterns = [
    # Admin (optional)
    path('admin/', admin.site.urls),

    # Accounts routes (login, logout, profile)
    path('accounts/', include('accounts.urls', namespace='accounts')),

    # Make the dashboard available at the site root
    path('', accounts_views.dashboard_view, name='dashboard'),
]
