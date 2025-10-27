
from django.urls import path

from main import views

app_name = "main"

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.log_in, name="login"),
    path("logout", views.log_out, name="logout"),
    path("singup", views.singup, name="singup"),
    path("new_cipher", views.new_cipher, name="new_cipher"),
    path("my_ciphers", views.my_ciphers, name="my_ciphers"),
    path("download_cipher/<int:cipher_id>", views.download_cipher, name="download_cipher"),
]
