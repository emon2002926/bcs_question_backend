from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView, LoginView, LogoutView, ProfileView,
    VerifyOTPView, ResendVerificationOTPView, ForgotPasswordView, 
    VerifyResetOTPView, ResetPasswordView, ChangePasswordView
)

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('verify-otp/', VerifyOTPView.as_view()),
    path('resend-verification-otp/', ResendVerificationOTPView.as_view()),
    path('login/', LoginView.as_view()),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view()),
    path('profile/', ProfileView.as_view()),
    path('change-password/', ChangePasswordView.as_view()),
    path('forgot-password/', ForgotPasswordView.as_view()),
    path('verify-reset-otp/', VerifyResetOTPView.as_view()),
    path('reset-password/', ResetPasswordView.as_view()),
]