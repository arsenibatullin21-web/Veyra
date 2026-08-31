from idlelib.rpc import request_queue

from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView

from users.forms import UserRegisterForm, UserLoginForm, UserProfileEditForm, UserPasswordChangeForm


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



class UserPasswordChange(LoginRequiredMixin, PasswordChangeView):
    form_class = UserPasswordChangeForm
    template_name = 'users/password_change.html'

    def get_success_url(self):
        return reverse_lazy('users:profile')
