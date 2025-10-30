from django.urls import path, include
from django.contrib import admin
from accounts import views as accounts_views

urlpatterns = [
    # Admin (optional)
    path('admin/', admin.site.urls),

    # Accounts routes (login, logout, profile)
    path('accounts/', include('accounts.urls', namespace='accounts')),

    # App url includes so their namespaces are registered for reversing
    path('support_records/', include('support_records.urls', namespace='support_records')),
    path('asset_management/', include('asset_management.urls', namespace='asset_management')),
    path('vendor_assistance/', include('vendor_assistance.urls', namespace='vendor_assistance')),
    path('thermal_rolls/', include('thermal_rolls.urls', namespace='thermal_rolls')),

    # Make the dashboard available at the site root
    path('', accounts_views.dashboard_view, name='dashboard'),
    # Convenience root-level login path (so /login works)
    path('login/', accounts_views.CustomLoginView.as_view(), name='login'),
]
