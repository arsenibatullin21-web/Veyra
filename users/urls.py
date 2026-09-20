from django.contrib.auth.views import LogoutView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, \
    PasswordResetCompleteView
from django.urls import path, reverse_lazy
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users import views

app_name = 'users'

urlpatterns = [
    path('register/', views.UserRegisterView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('logout/', LogoutView.as_view(next_page='users:login'), name='logout'),

    path('password-reset/', PasswordResetView.as_view(template_name='users/password_reset_form.html', success_url=reverse_lazy('users:password-reset-done'), email_template_name='users/password_reset_email.html'), name='password-reset'),
    path('password-reset/done/', PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'), name='password-reset-done'),
    path('password-reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html', success_url=reverse_lazy('users:password-reset-complete')), name='password-reset-confirm'),
    path('password-reset/complete/', PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'), name='password-reset-complete'),

    path('api/v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/register/', views.UserRegisterAPIView.as_view(), name='api-register'),
    path('api/v1/login/', views.UserLoginAPIView.as_view(), name='api-login'),
    path('api/v1/profile/', views.UserProfileAPIView.as_view(), name='api-profile'),
    path('api/v1/changepassword/', views.ChangePasswordAPIView.as_view(), name='api-change-password'),
    path('api/v1/logout/', views.logout_view, name='api-logout')
]
