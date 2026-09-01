from django.contrib.auth import get_user_model, update_session_auth_hash, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.shortcuts import redirect, render
from django.template.context_processors import request
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView
from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_200_OK
from rest_framework_simplejwt.tokens import RefreshToken

from users.forms import UserRegisterForm, UserLoginForm, UserProfileEditForm, UserPasswordChangeForm
from users.serializers import UserRegisterSerializer, UserProfileSerializer, UserLoginSerializer, \
    UserProfileEditSerializer, ChangePasswordSerializer


# Create your views here.

class UserRegisterView(CreateView):
    model = get_user_model()
    form_class = UserRegisterForm
    template_name = 'users/register.html'

    def get_success_url(self):
        return reverse_lazy('users:login')

class UserLoginView(LoginView):
    model = get_user_model()
    form_class = UserLoginForm
    template_name = 'users/login.html'

    def get_success_url(self):
        return reverse_lazy('users:profile')

class UserProfileView(LoginRequiredMixin, DetailView):
    model = get_user_model()
    context_object_name = 'profile_user'
    template_name = 'users/profile.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = UserProfileEditForm(instance=self.request.user)
        context['password_form'] = UserPasswordChangeForm(user=self.request.user)
        return context

    def post(self, request, *args, **kwargs):
        form_type = request.POST.get('form_type')

        if form_type == 'profile':
            form = UserProfileEditForm(
                request.POST,
                request.FILES,
                instance=request.user,
            )

            if form.is_valid():
                form.save()
                messages.success(request, 'Profile updated successfully.')
                return redirect('users:profile')

            self.object = self.get_object()
            context = self.get_context_data()
            context['form'] = form
            context['is_editing'] = True
            return self.render_to_response(context)

        if form_type == 'password':
            profile_form = UserProfileEditForm(instance=request.user)
            form = UserPasswordChangeForm(
                data=request.POST,
                user=request.user,
            )

            if form.is_valid():
                request.user.set_password(form.cleaned_data.get('new_password1'))
                request.user.save()
                update_session_auth_hash(request, request.user)
                return redirect('users:profile')

            self.object = self.request.user
            context = self.get_context_data()
            context['is_password_editing'] = True
            context['form'] = profile_form
            context['password_form'] = form
            return self.render_to_response(context)



class UserRegisterAPIView(generics.CreateAPIView):
    model = get_user_model()
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny, ]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            user = serializer.save()

            refresh = RefreshToken.for_user(user)

            return Response({
                'user': UserProfileSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'message': 'You registered in successfully.'
            }, status=HTTP_201_CREATED)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class UserLoginAPIView(generics.GenericAPIView):
    model = get_user_model()
    serializer_class = UserLoginSerializer
    permission_classes = [permissions.AllowAny, ]

    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.validated_data.get('user')
            login(request, user=user)

            refresh = RefreshToken.for_user(user)

            return Response({
                'user': UserProfileSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'message': "You logged in successfully."
            }, status=HTTP_200_OK)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

class UserProfileAPIView(generics.RetrieveUpdateAPIView):
    model = get_user_model()
    permission_classes = [permissions.IsAuthenticated, ]

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserProfileEditSerializer
        return UserProfileSerializer

class ChangePasswordAPIView(generics.UpdateAPIView):
    model = get_user_model()
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        partial = kwargs.get('partial', False)
        serializer = self.get_serializer(instance=self.get_object(), data=request.data, partial=partial)

        if serializer.is_valid(raise_exception=True):
            serializer.save()

            return Response({
                "user": str(self.get_object().username),
                "message": "Password was changed successfully."
            }, status=HTTP_200_OK)

        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, ])
def logout_view(request):
    try:
        refresh = request.data.get('refresh_token')
        if refresh:
            token = RefreshToken(refresh)
            token.blacklist()
            return Response({
                'user': str(request.user.username),
                'message': "You logged out successfully."
            }, status=HTTP_200_OK)
    except Exception as e:
        return Response({
            'error': 'Something went wrong.'
        }, status=HTTP_400_BAD_REQUEST)

