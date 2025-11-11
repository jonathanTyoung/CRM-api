from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from api.views.auth import register_user, login_user

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/register/', register_user),
    path('api/login/', login_user),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
