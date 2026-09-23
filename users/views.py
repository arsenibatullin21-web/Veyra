from django.conf import settings
from django.contrib.auth import get_user_model, update_session_auth_hash, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render, get_object_or_404
from django.core.mail import send_mail
from django.urls import reverse_lazy, reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views import View
from django.views.generic import CreateView, DetailView, UpdateView
from django.utils.encoding import force_bytes, force_str
from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_200_OK
from rest_framework_simplejwt.tokens import RefreshToken

from users.forms import UserRegisterForm, UserLoginForm, UserProfileEditForm, UserPasswordChangeForm
from users.serializers import UserRegisterSerializer, UserProfileSerializer, UserLoginSerializer, \
    UserProfileEditSerializer, ChangePasswordSerializer
from users.tasks import send_activation_email, send_password_changed_email


# Create your views here.

class UserRegisterView(CreateView):
    model = get_user_model()
    form_class = UserRegisterForm
    template_name = 'users/register.html'

    def get_success_url(self):
        return reverse_lazy('users:login')

    def form_valid(self, form):
        user = form.save(commit=False)

        user.is_active = False
        user.save()

        protocol = 'https' if self.request.is_secure() else 'http'
        domain = self.request.get_host()

        transaction.on_commit(
            lambda: send_activation_email.delay(
                user.pk,
                domain,
                protocol
            )
        )
        messages.success(
            self.request,
            'We sent an activation link to your email.'
        )
        return HttpResponseRedirect(
            self.get_success_url()
        )

class ActivationView(View):
    def get(self, request, uidb64, token):
        try:
            user_id = force_str(
                urlsafe_base64_decode(
                    uidb64
                )
            )

            user = get_user_model().objects.get(pk=user_id)
        except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
            user = None

        if user is not None and user.is_active == False and default_token_generator.check_token(user, token=token):
            user.is_active = True
            user.save(update_fields=['is_active'])
            messages.success(request, 'Your account was activated successfully.')
            return redirect('users:login')

        messages.error(
            request,
            'This activation link is invalid or has already been used.'
        )
        return redirect('users:register')



class UserLoginView(LoginView):
    model = get_user_model()
    form_class = UserLoginForm
    template_name = 'users/login.html'

    def get_success_url(self):
        return self.get_redirect_url() or reverse_lazy('users:profile')

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
                transaction.on_commit(
                    lambda: send_password_changed_email.delay(
                        self.request.user.pk,
                    )
                )
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
            user = serializer.save(is_active=False)
            protocol = 'http' if self.request.is_secure() else 'http'
            domain = self.request.get_host()

            transaction.on_commit(
                lambda: send_activation_email.delay(
                    user_id=user.pk,
                    domain=domain,
                    protocol=protocol
                )
            )


            return Response({
                'user': UserProfileSerializer(user).data,
                'message': 'We sent you activation link.'
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

            transaction.on_commit(
                lambda: send_password_changed_email.delay(
                    self.get_object().pk
                )
            )
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


