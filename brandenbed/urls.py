from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import set_language

urlpatterns = [
    path("admin/", admin.site.urls),
    path("set_language/", set_language, name="set_language"),  # Language switching
]

# Internationalized URLs
urlpatterns += i18n_patterns(
    # Core
    path("", include("core.urls")),  # Landing page / main site

    # Accounts / Auth
    path("accounts/", include("accounts.urls")),

    # Employees
    path("employees/", include("employees.urls")),

    # Properties
    path("properties/", include("properties.urls")),

    # Landlords
    path("landlords/", include("landlords.urls")),

    # Residents
    path("residents/", include("residents.urls")),

    # Leads
    path("leads/", include("leads.urls")),

    # Payments
    path("payments/", include("payments.urls")),

    # Support
    path("support/", include("support.urls")),

    # Maintenance
    path("maintenance/", include("maintenance.urls")),

    # Housekeeping
    path("housekeeping/", include("housekeeping.urls")),

    # Reports
    path("reports/", include("reports.urls")),

    # Dashboard
    path("dashboard/", include("dashboard.urls")),

    prefix_default_language=False,
)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)