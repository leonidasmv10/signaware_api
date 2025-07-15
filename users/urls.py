from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import * 
from .views import PasswordResetConfirmView
urlpatterns = [
    path('test/', TestView.as_view(), name='user_test'),
    path('register/', RegisterAPIView.as_view(), name='user_register'),
    path('login/', TokenObtainPairView.as_view(), name='user_login'),
    path('logout/', LogoutAPIView.as_view(), name='user_logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("recover-password/", PasswordResetRequestView.as_view(), name="password_reset_request"),
    path("reset-password/<uidb64>/<token>/", PasswordResetConfirmView.as_view(), name="reset-password"),

    path('profile/', ProfileView.as_view(), name='user_profile'),
    path('delete/', DeleteUserView.as_view(), name='user_delete'), 
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('validate-token/', ValidateTokenView.as_view(), name='validate_token'),
]
