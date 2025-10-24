from django.contrib.auth.hashers import (
    BasePasswordHasher,
)

from main.utils.stribog import stribog_hash


class StribogHasher(BasePasswordHasher):
    algorithm = "stribog"

    def encode(self, password, salt=None, iteration=None):
        clean_hash = stribog_hash(password, 512)
        return f"{self.algorithm}${clean_hash}"

    def verify(self, password, encoded):
        check_hash = self.encode(password)
        return encoded == check_hash
