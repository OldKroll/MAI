import pyotp

from datetime import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models

from main.enums import CipherType


class User(AbstractUser):
    password = models.CharField(max_length=2048, null=False)
    otp_secret_app = models.CharField(max_length=64, null=False, default=pyotp.random_base32)
    otp_secret_email = models.CharField(max_length=64, null=False, default=pyotp.random_base32)
    otp_app = models.BooleanField(default=False)


class Cipher(models.Model):
    id = models.AutoField(primary_key=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="author")
    cipher_type = models.CharField(max_length=16, choices=[(ct.name, ct.value) for ct in CipherType])
    text = models.TextField()
    ciphered = models.TextField()
