from django.contrib.auth.views import LogoutView
from django.urls import path
from users import views

app_name = 'users'

urlpatterns = [
    path('register/', views.UserRegisterView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('changepassword/', views.UserPasswordChange.as_view(), name='password_change'),
    path('logout/', LogoutView.as_view(next_page='users:login'), name='logout')
]
