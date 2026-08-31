from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UsernameField, AuthenticationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


class UserRegisterForm(UserCreationForm):
    username = UsernameField(
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Choose a username',
            'autocomplete': 'username',
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'you@example.com',
            'autocomplete': 'email',
        })
    )
    password1 = forms.CharField(
        required=True,
        validators=[validate_password, ],
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Create a password',
            'autocomplete': 'new-password',
        })
    )
    password2 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Repeat your password',
            'autocomplete': 'new-password',
        })
    )

    class Meta:
        model = get_user_model()
        fields = ['username','email', 'password1', 'password2']

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if username and get_user_model().objects.filter(username=username).exists():
            raise forms.ValidationError('Username already exists.')
        if email and get_user_model().objects.filter(email=email).exists():
            raise forms.ValidationError('Email already exists.')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Passwords do not match.')
        return cleaned_data


class UserLoginForm(AuthenticationForm):
    username = UsernameField(
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter username or email',
            'autocomplete': 'username',
        })
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter your password',
            'autocomplete': 'current-password',
        })
    )

    class Meta:
        model = get_user_model()
        fields = ['email', 'password']

class UserPasswordChangeForm(forms.Form):
    old_password = forms.CharField(required=True)
    new_password1 = forms.CharField(required=True)
    new_password2 = forms.CharField(required=True)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        old_password = cleaned_data.get('old_password')
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')

        if not self.user.check_password(old_password):
            raise forms.ValidationError('Old password is incorrect.')

        if new_password1 != new_password2:
            raise forms.ValidationError('New passwords do not match.')

        if old_password == new_password1:
            raise forms.ValidationError('Old and new password cant be similar.')

        return cleaned_data

class UserProfileEditForm(forms.ModelForm):

    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'phone', 'avatar', 'city', 'address']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'placeholder': 'First name',
                'autocomplete': 'given-name',
            }),
            'last_name': forms.TextInput(attrs={
                'placeholder': 'Last name',
                'autocomplete': 'family-name',
            }),
            'phone': forms.TextInput(attrs={
                'placeholder': '+1 555 000 0000',
                'autocomplete': 'tel',
            }),
            'city': forms.TextInput(attrs={
                'placeholder': 'City',
                'autocomplete': 'address-level2',
            }),
            'address': forms.TextInput(attrs={
                'placeholder': 'Street, building, apartment',
                'autocomplete': 'street-address',
            }),
        }

