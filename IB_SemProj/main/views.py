from datetime import datetime
from django.http import FileResponse, HttpRequest
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import pyotp
from fpdf import FPDF
from main.enums import CipherType
from main.forms import LoginForm, SignUpForm
from main.models import Cipher, User
from main.utils.emailer import send_otp_code
from main.utils.kuznechik import kuznechik_encrypt
from main.utils.rsa import RSA
from django.core.files.base import ContentFile
from pyhanko.pdf_utils.reader import PdfFileReader
from pyhanko.sign import signers
from io import BytesIO
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.sign import fields, signers
from pyhanko import stamp


def index(request: HttpRequest):
    return render(request, template_name="index.html")


def log_in(request: HttpRequest):
    if request.method == "POST":
        step = request.session.get("step", 1)
        print(step)
        if step == 1:
            form = LoginForm(data=request.POST)
            if form.is_valid():
                user: User = authenticate(
                    username=form.cleaned_data["username"],
                    password=form.cleaned_data["password"],
                )
                if user is not None:
                    request.session["step"] = 2
                    request.session["username"] = form.cleaned_data["username"]
                    if not user.otp_app:
                        otp_url = pyotp.totp.TOTP(user.otp_secret_app).provisioning_uri(
                            name=user.username, issuer_name="Cipher"
                        )
                        user.otp_app = True
                        user.save()
                    else:
                        otp_url = None
                    return render(
                        request, "login.html", context={"step": 2, "otp_url": otp_url}
                    )
            else:
                return render(request, "login.html", context={"err": True})
        elif step == 2:
            user = User.objects.get(username=request.session["username"])
            if pyotp.TOTP(user.otp_secret_app).verify(request.POST.get("otp_code", 0)):
                request.session["step"] = 3
                send_otp_code(user.email, pyotp.TOTP(user.otp_secret_email, interval=180).now())
                return render(request, "login.html", context={"step": 3})
            else:
                return render(request, "login.html", context={"step": 2, "err": True})
        elif step == 3:
            user = User.objects.get(username=request.session["username"])
            if pyotp.TOTP(user.otp_secret_email, interval=180).verify(
                request.POST.get("otp_code", 0)
            ):
                del request.session["step"]
                del request.session["username"]
                login(request, user)
                return redirect("/")
            else:
                return render(request, "login.html", context={"step": 3, "err": True})
    request.session["step"] = 1
    return render(request, "login.html", context={"step": 1})


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


@login_required(login_url="/login")
def download_cipher(request: HttpRequest, cipher_id: int):
    cipher = get_object_or_404(Cipher, id=cipher_id, author=request.user)
    doc = FPDF()
    doc.add_page()
    doc.set_text_shaping(True)
    doc.add_font(
        family="dejavu-sans-mono", style="", fname="main/utils/fonts/DejaVuSansMono.ttf"
    )
    doc.set_font(family="dejavu-sans-mono", style="", size=12)
    text = f"""
    Шифр №{cipher.id}
    Автор: {cipher.author.username}
    Метод шифрования: {cipher.cipher_type}
    Текст: {cipher.text}
    Шифровка: {cipher.ciphered}
    """

    for txt in text.split("\n"):
        doc.write(8, txt)
        doc.ln(8)
    file_binary = doc.output()

    ipdw = IncrementalPdfFileWriter(
        BytesIO(file_binary), prev=PdfFileReader(BytesIO(file_binary))
    )
    fields.append_signature_field(
        ipdw, fields.SigFieldSpec("CipherSig", box=(200, 600, 400, 660))
    )
    pdf_signer = signers.PdfSigner(
        signers.PdfSignatureMetadata(field_name="CipherSig"),
        signer=signers.SimpleSigner.load_pkcs12(
            pfx_file="main/utils/crypto/Cipher.p12", passphrase=b"cipher"
        ),
        stamp_style=stamp.TextStampStyle(
            stamp_text=f"Signed by: %(signer)s\nTime: {datetime.now().isoformat()}"
        ),
    )
    out = pdf_signer.sign_pdf(ipdw, existing_fields_only=True)
    response = FileResponse(
        ContentFile(content=out.read(), name=f"cipher_{cipher.id}.pdf")
    )
    return response
