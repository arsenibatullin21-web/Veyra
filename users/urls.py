from django.contrib.auth.views import LogoutView
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users import views

app_name = 'users'

urlpatterns = [
    path('register/', views.UserRegisterView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('logout/', LogoutView.as_view(next_page='users:login'), name='logout'),

    path('api/v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/register/', views.UserRegisterAPIView.as_view(), name='api-register'),
    path('api/v1/login/', views.UserLoginAPIView.as_view(), name='api-login'),
    path('api/v1/profile/', views.UserProfileAPIView.as_view(), name='api-profile'),
    path('api/v1/changepassword/', views.ChangePasswordAPIView.as_view(), name='api-change-password'),
    path('api/v1/logout/', views.logout_view, name='api-logout')
]
