from rest_framework.routers import DefaultRouter
from django.contrib import admin
from django.urls import include, path, re_path
from accounts import views as account_views


"""
URL configuration for access_manager_api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

router = DefaultRouter()

# accounts
router.register(
    r"users",
    account_views.CustomUserViewSet,
    basename="user",
)
router.register(
    r"organizations",
    account_views.OrganizationViewSet,
    basename="organization",
)
router.register(
    r"groups",
    account_views.CustomGroupViewSet,
    basename="group",
)
router.register(
    r"environments",
    account_views.EnvironmentViewSet,
    basename="environment",
)

urlpatterns = [
    path("admin/", admin.site.urls),
    re_path(r"api/v1/auth/", include("durin.urls")),
    re_path(r"api/v1/", include(router.urls)),
]
