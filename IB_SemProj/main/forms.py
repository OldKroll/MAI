from django import forms
from main.models import User
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        max_length=254, help_text="Обязательное поле. Введите действующий email."
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Имя пользователя")
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)
