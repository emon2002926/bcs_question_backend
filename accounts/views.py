from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from django.core.mail import send_mail
from django.conf import settings
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
        if serializer.is_valid():
            user = serializer.save()
            otp = OTP.objects.create(user=user)
            otp.generate_code()
            send_mail(
                'Verify your account',
                f'Your OTP is: {otp.code}',
                settings.EMAIL_HOST_USER,
                [user.email],
            )
            return Response({'message': 'OTP sent to your email'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTPView(APIView):
    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            code = serializer.validated_data['code']
            try:
                user = User.objects.get(email=email)
                otp = OTP.objects.filter(user=user, code=code).last()
                if not otp:
                    return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
                
                if otp.is_expired():
                    return Response({'error': 'OTP has expired'}, status=status.HTTP_400_BAD_REQUEST)

                user.is_active = True
                user.is_verified = True
                user.save()
                otp.delete()
                refresh = RefreshToken.for_user(user)
                return Response({
                    'message': 'Account verified',
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                })
            except User.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password']
            )
            if user:
                if not user.is_verified:
                    return Response({'error': 'Please verify your email first'}, status=status.HTTP_403_FORBIDDEN)
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                })
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Logged out'})
        except Exception:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            'email': request.user.email,
            'username': request.user.username,
            'is_verified': request.user.is_verified,
        })


class ResendVerificationOTPView(APIView):
    def post(self, request):
        serializer = ResendVerificationOTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
                
                if user.is_verified:
                    return Response({'error': 'User is already verified.'}, status=status.HTTP_400_BAD_REQUEST)
                
                last_otp = OTP.objects.filter(user=user).last()
                if last_otp and not last_otp.can_resend():
                    return Response({'error': 'Please wait 60 seconds before requesting a new OTP.'}, status=status.HTTP_429_TOO_MANY_REQUESTS)
                
                OTP.objects.filter(user=user).delete()
                otp = OTP.objects.create(user=user)
                otp.generate_code()
                
                send_mail(
                    'Verify your account',
                    f'Your new OTP is: {otp.code}',
                    settings.EMAIL_HOST_USER,
                    [user.email],
                )
                return Response({'message': 'A new OTP has been sent to your email.'})
            except User.DoesNotExist:
                return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ForgotPasswordView(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
                
                last_otp = PasswordResetOTP.objects.filter(user=user).last()
                if last_otp and not last_otp.can_resend():
                    return Response({'error': 'Please wait 60 seconds before requesting a new OTP.'}, status=status.HTTP_429_TOO_MANY_REQUESTS)
                
                PasswordResetOTP.objects.filter(user=user).delete()
                otp = PasswordResetOTP.objects.create(user=user)
                otp.generate_code()
                send_mail(
                    'Password Reset OTP',
                    f'Your password reset OTP is: {otp.code}',
                    settings.EMAIL_HOST_USER,
                    [user.email],
                )
                return Response({'message': 'OTP sent to your email'})
            except User.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyResetOTPView(APIView):
    def post(self, request):
        serializer = VerifyResetOTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            code = serializer.validated_data['code']
            try:
                user = User.objects.get(email=email)
                otp = PasswordResetOTP.objects.filter(user=user, code=code, is_used=False).last()

                if not otp:
                    return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)

                if otp.is_expired():
                    return Response({'error': 'OTP has expired'}, status=status.HTTP_400_BAD_REQUEST)

                return Response({'message': 'OTP verified successfully'}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            code = serializer.validated_data['code']
            new_password = serializer.validated_data['new_password']
            try:
                user = User.objects.get(email=email)
                otp = PasswordResetOTP.objects.filter(user=user, code=code, is_used=False).last()

                if not otp:
                    return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)

                if otp.is_expired():
                    return Response({'error': 'OTP has expired'}, status=status.HTTP_400_BAD_REQUEST)

                user.set_password(new_password)
                user.save()

                otp.is_used = True
                otp.save()

                return Response({'message': 'Password reset successful'}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            old_password = serializer.validated_data['old_password']
            new_password = serializer.validated_data['new_password']

            if not user.check_password(old_password):
                return Response({'error': 'Old password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(new_password)
            user.save()
            return Response({'message': 'Password changed successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)