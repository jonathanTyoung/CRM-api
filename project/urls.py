from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from api.views.auth import register_user, login_user, current_user
from api.views.agent_profiles import AgentProfileViewSet
from api.views.contacts import ContactViewSet
from api.views.leads import LeadViewSet
from api.views.opportunities import OpportunityViewSet
from api.views.meta import list_sources, list_tags
from rest_framework import routers

router = routers.DefaultRouter(trailing_slash=False)
router.register(r"agent-profiles", AgentProfileViewSet, basename="agent-profiles")
router.register(r"contacts", ContactViewSet, basename="contact")
router.register(r"leads", LeadViewSet, basename="lead")
router.register(r"opportunities", OpportunityViewSet, basename="opportunity")

urlpatterns = [
    path("admin/", admin.site.urls),

    # AUTH FIRST
    path("api/register/", register_user),
    path("api/login/", login_user),
    path("api/current_user/", current_user),
    path("api/token/refresh/", TokenRefreshView.as_view()),

    # META
    path("api/tags/", list_tags),
    path("api/sources/", list_sources),

    # ROUTER LAST  ← 🔥 IMPORTANT
    path("api/", include(router.urls)),
]
