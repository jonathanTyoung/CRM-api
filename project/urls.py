from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework import routers
from api.views.auth import register_user, login_user, current_user
from api.views.agent_profiles import AgentProfileViewSet

router = routers.DefaultRouter(trailing_slash=False)
router.register(r"agent-profiles", AgentProfileViewSet, basename="agent-profiles")

urlpatterns = [
    path("", include(router.urls)),
    path('admin/', admin.site.urls, name='admin'),
    path('api/register/', register_user, name='register_user'),
    path('api/login/', login_user, name='login_user'),
    path('api/current_user/', current_user, name='current_user'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
