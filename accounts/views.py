from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.shortcuts import render, redirect
from django.contrib import messages
from django.template import loader
from django.urls import reverse_lazy

from .forms import RegisterForm, LoginForm, UserUpdateForm, CustomPasswordResetForm, CustomSetPasswordForm


def home_view(request):
    return render(request, 'home.html')

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
            form = RegisterForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Błędny login lub hasło')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

class MyPasswordResetView(PasswordResetView):
    template_name = 'reset_password.html'
    form_class = CustomPasswordResetForm
    success_url = reverse_lazy('password_reset_done')

class MyPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'reset_password_form.html'
    form_class = CustomSetPasswordForm
    success_url = reverse_lazy('password_reset_complete')

@login_required(login_url='login')
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def user_view(request):
    user = request.user
    return render(request, 'user.html', {'user': user})

@login_required(login_url='login')
def user_update_view(request):
    user = request.user
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user')
    else:
        form = UserUpdateForm(instance=user)

    return render(request, 'edit_user.html', {'form': form})
