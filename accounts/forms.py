from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm, SetPasswordForm


# Rejestracja
class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        label='Email',
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'}))

    username = forms.CharField(
        label='Nazwa użytkownika',
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}))

    password1 = forms.CharField(
        label='Hasło',
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    password2 = forms.CharField(
        label='Powtórz hasło',
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

# Logowanie
class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Nazwa użytkownika',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    password = forms.CharField(
        label='Hasło',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label='Email',
        max_length=254,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label='Nowe hasło',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password2 = forms.CharField(
        label='Powtórz nowe hasło',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

# Aktualizacja danych użytkownika
class UserUpdateForm(forms.ModelForm):
    username = forms.CharField(
        label='Nazwa użytkownika',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'email']