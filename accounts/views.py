from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib.auth import authenticate, get_user_model
from django.core.mail import send_mail
from django.conf import settings
from core.utils import send_response, send_error
from .serializers import (
    RegisterSerializer, LoginSerializer, OTPVerifySerializer,
    ResendVerificationOTPSerializer, ForgotPasswordSerializer, 
    VerifyResetOTPSerializer, ResetPasswordSerializer, ChangePasswordSerializer
)
from .models import OTP, PasswordResetOTP

User = get_user_model()


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        OTP.objects.filter(user=user).delete()
        otp = OTP.objects.create(user=user)
        otp.generate_code()
        send_mail(
            'Verify your account',
            f'Your OTP is: {otp.code}',
            settings.EMAIL_HOST_USER,
            [user.email],
        )
        return send_response(
            success=True,
            message="OTP sent to your email",
            data=None,
            status_code=status.HTTP_201_CREATED
        )


class VerifyOTPView(APIView):
    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        code = serializer.validated_data['code']
        try:
            user = User.objects.get(email=email)
            otp = OTP.objects.filter(user=user, code=code).last()
            if not otp:
                return send_error(message="Invalid OTP", path="code", status_code=status.HTTP_400_BAD_REQUEST)
            
            if otp.is_expired():
                return send_error(message="OTP has expired", path="code", status_code=status.HTTP_400_BAD_REQUEST)

            user.is_active = True
            user.is_verified = True
            user.save()
            otp.delete()
            refresh = RefreshToken.for_user(user)
            return send_response(
                success=True,
                message="Account verified successfully",
                data={
                    "token": str(refresh.access_token),
                    "refresh": str(refresh),
                    "user_info": {
                        "id": user.id,
                        "email": user.email,
                        "username": user.username,
                        "is_verified": user.is_verified,
                    }
                },
                status_code=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return send_error(message="User not found", path="email", status_code=status.HTTP_404_NOT_FOUND)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password']
        )
        if user:
            if not user.is_verified:
                return send_error(message="Please verify your email first", path="email", status_code=status.HTTP_403_FORBIDDEN)
            refresh = RefreshToken.for_user(user)
            return send_response(
                success=True,
                message="Login successfully",
                data={
                    "token": str(refresh.access_token),
                    "refresh": str(refresh),
                    "user_info": {
                        "id": user.id,
                        "email": user.email,
                        "username": user.username,
                        "is_verified": user.is_verified,
                    }
                },
                status_code=status.HTTP_200_OK
            )
        return send_error(message="Invalid credentials", path="", status_code=status.HTTP_401_UNAUTHORIZED)


class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        return send_response(
            success=True,
            message="Token refreshed successfully",
            data=response.data,
            status_code=response.status_code
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return send_error(message="Refresh token is required", path="refresh", status_code=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return send_response(
                success=True,
                message="Logged out successfully",
                data=None,
                status_code=status.HTTP_200_OK
            )
        except Exception:
            return send_error(message="Invalid or expired token", path="refresh", status_code=status.HTTP_400_BAD_REQUEST)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return send_response(
            success=True,
            message="Profile retrieved successfully",
            data={
                "user_info": {
                    "id": request.user.id,
                    "email": request.user.email,
                    "username": request.user.username,
                    "is_verified": request.user.is_verified,
                }
            },
            status_code=status.HTTP_200_OK
        )


class ResendVerificationOTPView(APIView):
    def post(self, request):
        serializer = ResendVerificationOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email)
            
            if user.is_verified:
                return send_error(message="User is already verified.", path="email", status_code=status.HTTP_400_BAD_REQUEST)
            
            last_otp = OTP.objects.filter(user=user).last()
            if last_otp and not last_otp.can_resend():
                return send_error(message="Please wait 60 seconds before requesting a new OTP.", path="", status_code=status.HTTP_429_TOO_MANY_REQUESTS)
            
            OTP.objects.filter(user=user).delete()
            otp = OTP.objects.create(user=user)
            otp.generate_code()
            
            send_mail(
                'Verify your account',
                f'Your new OTP is: {otp.code}',
                settings.EMAIL_HOST_USER,
                [user.email],
            )
            return send_response(
                success=True,
                message="A new OTP has been sent to your email.",
                data=None,
                status_code=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return send_error(message="User not found.", path="email", status_code=status.HTTP_404_NOT_FOUND)


class ForgotPasswordView(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email)
            
            last_otp = PasswordResetOTP.objects.filter(user=user).last()
            if last_otp and not last_otp.can_resend():
                return send_error(message="Please wait 60 seconds before requesting a new OTP.", path="", status_code=status.HTTP_429_TOO_MANY_REQUESTS)
            
            PasswordResetOTP.objects.filter(user=user).delete()
            otp = PasswordResetOTP.objects.create(user=user)
            otp.generate_code()
            send_mail(
                'Password Reset OTP',
                f'Your password reset OTP is: {otp.code}',
                settings.EMAIL_HOST_USER,
                [user.email],
            )
            return send_response(
                success=True,
                message="OTP sent to your email",
                data=None,
                status_code=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return send_error(message="User not found", path="email", status_code=status.HTTP_404_NOT_FOUND)


class VerifyResetOTPView(APIView):
    def post(self, request):
        serializer = VerifyResetOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        code = serializer.validated_data['code']
        try:
            user = User.objects.get(email=email)
            otp = PasswordResetOTP.objects.filter(user=user, code=code, is_used=False).last()

            if not otp:
                return send_error(message="Invalid OTP", path="code", status_code=status.HTTP_400_BAD_REQUEST)

            if otp.is_expired():
                return send_error(message="OTP has expired", path="code", status_code=status.HTTP_400_BAD_REQUEST)

            return send_response(
                success=True,
                message="OTP verified successfully",
                data=None,
                status_code=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return send_error(message="User not found", path="email", status_code=status.HTTP_404_NOT_FOUND)


class ResetPasswordView(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        code = serializer.validated_data['code']
        new_password = serializer.validated_data['new_password']
        try:
            user = User.objects.get(email=email)
            otp = PasswordResetOTP.objects.filter(user=user, code=code, is_used=False).last()

            if not otp:
                return send_error(message="Invalid OTP", path="code", status_code=status.HTTP_400_BAD_REQUEST)

            if otp.is_expired():
                return send_error(message="OTP has expired", path="code", status_code=status.HTTP_400_BAD_REQUEST)

            user.set_password(new_password)
            user.save()

            otp.is_used = True
            otp.save()

            return send_response(
                success=True,
                message="Password reset successful",
                data=None,
                status_code=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return send_error(message="User not found", path="email", status_code=status.HTTP_404_NOT_FOUND)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        old_password = serializer.validated_data['old_password']
        new_password = serializer.validated_data['new_password']

        if not user.check_password(old_password):
            return send_error(message="Old password is incorrect", path="old_password", status_code=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return send_response(
            success=True,
            message="Password changed successfully",
            data=None,
            status_code=status.HTTP_200_OK
        )