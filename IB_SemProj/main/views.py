from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from main.enums import CipherType
from main.forms import LoginForm, SignUpForm
from main.models import Cipher
from main.utils.kuznechik import kuznechik_encrypt
from main.utils.rsa import RSA

# Create your views here.


def index(request: HttpRequest):
    return render(request, template_name="index.html")

def log_in(request: HttpRequest):
    if request.method == "POST":
        step = request.session.get('step', 1)
        print(step)
        if step == 1:
            form = LoginForm(data=request.POST)
            if form.is_valid():
                user = authenticate(
                    username=form.cleaned_data["username"],
                    password=form.cleaned_data["password"],
                )
                if user is not None:
                    request.session['step'] = 2
                    return render(request, "login.html", context={"step": 2})
                    # login(request, user)
                    # return redirect("/")
            else:
                return render(request, "login.html", context={"err": True})
        elif step == 2:
            request.session['step'] = 3
            return render(request, "login.html", context={"step": 3})
        elif step == 3:
            pass
        else:
            pass
    request.session['step'] = 1
    return render(request, "login.html")

@login_required(login_url="/login")
def log_out(request: HttpRequest):
    logout(request)
    return redirect("/")


def singup(request: HttpRequest):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/login")
        else:
            return render(
                request, "singup.html", context={"err": True, "detail": form.errors}
            )
    return render(request, "singup.html")


@login_required(login_url="/login")
def new_cipher(request: HttpRequest):
    if request.method == "POST":
        new_cipher = Cipher()
        new_cipher.author = request.user
        new_cipher.cipher_type = request.POST["cipher_type"]
        new_cipher.text = request.POST["text"]
        match request.POST["cipher_type"]:
            case CipherType.RSA:
                rsa = RSA()
                rsa.gen_keys(2048)
                new_cipher.ciphered = rsa.encrypt(request.POST["text"])
            case CipherType.KUZNECHIK:
                new_cipher.ciphered = kuznechik_encrypt(request.POST["text"])
            case _:
                return render(request, "new_cipher.html", context={"err": True})
        new_cipher.save()
        return redirect("/my_ciphers")
    return render(request, "new_cipher.html")


@login_required(login_url="/login")
def my_ciphers(request: HttpRequest):
    ciphers_list = Cipher.objects.filter(author=request.user.id).all()
    return render(request, "my_ciphers.html", context={"ciphers_list": ciphers_list})
