from django.contrib.auth.hashers import (
    BasePasswordHasher,
)

from main.utils.stribog import Stribog, stribog_hex_to_str, hexdec, str_to_hexstr


class StribogHasher(BasePasswordHasher):
    algorithm = "stribog"

    def encode(self, password, salt=None, iteration=None):
        clean_hash = stribog_hex_to_str(Stribog(hexdec(str_to_hexstr(password))[::-1]).digest())
        return f"{self.algorithm}${clean_hash}"

    def verify(self, password, encoded):
        check_hash = self.encode(password)
        return encoded == check_hash
