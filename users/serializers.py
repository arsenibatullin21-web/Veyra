from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from django.contrib.auth import authenticate


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=True, write_only=True, validators=[validate_password, ])
    password_confirm = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'username', 'email', 'phone', 'password', 'password_confirm','avatar', 'address', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def validate(self, attrs):
        password = attrs.get('password')
        password_confirm = attrs.get('password_confirm')
        username = attrs.get('username')
        email = attrs.get('email')

        if password != password_confirm:
            raise serializers.ValidationError({
                'errors': 'Passwords do not match.'
            })

        if get_user_model().objects.filter(username=username).exists():
            raise serializers.ValidationError({
                'errors': 'Username is already exists.'
            })

        if get_user_model().objects.filter(email=email).exists():
            raise serializers.ValidationError({
                'errors': 'Email is already exists.'
            })

        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = get_user_model().objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(self.context['request'], username=username, password=password)

            if not user:
                raise serializers.ValidationError({
                    'errors': 'User is not found.'
                })

            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError({
                'errors': 'Email or password cant be empty.'
            })


class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'phone', 'email', 'avatar', 'city', 'address', 'created_at']


class UserProfileEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'phone', 'avatar', 'city', 'address']

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, validators=[validate_password, ])
    new_password_confirm = serializers.CharField(required=True, write_only=True)

    def validate_old_password(self, value):
        if not self.context.get('request').user.check_password(value):
            raise serializers.ValidationError({
                'errors': 'Old password is incorrect.'
            })
        return value

    def validate(self, attrs):
        new_password = attrs.get('new_password')
        new_password_confirm = attrs.get('new_password_confirm')

        if new_password_confirm != new_password:
            raise serializers.ValidationError({
                'errors': 'Passwords do not match.'
            })
        return attrs

    def save(self, **kwargs):
        user = self.context.get('request').user
        user.set_password(self.validated_data.get('new_password'))
        user.save()
        return user



