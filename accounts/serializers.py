from rest_framework import serializers
from django.contrib.auth import get_user_model
 
User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        user.is_active = False
        user.save()
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

class OTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)    


class ResendVerificationOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class VerifyResetOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(min_length=6)


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=False)
    old_password = serializers.CharField(required=False)
    new_password = serializers.CharField(required=True, min_length=6)
    confirm_password = serializers.CharField(required=False)

    def validate(self, data):
        current_pass = data.get('current_password') or data.get('old_password')
        if not current_pass:
            raise serializers.ValidationError({"current_password": "This field is required."})
        data['current_password'] = current_pass

        if data.get('confirm_password') and data.get('confirm_password') != data.get('new_password'):
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})

        if current_pass == data.get('new_password'):
            raise serializers.ValidationError({"new_password": "New password cannot be the same as current password."})

        return data    