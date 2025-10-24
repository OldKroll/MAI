"""
Модуль генерации RSA ключей
"""

import math
from main.utils.rsa.prime_generator import generate_large_prime


def generate_rsa(length: int = 1024) -> dict:
    """
    Метод генерации ключа
    """
    p = generate_large_prime(length)
    q = generate_large_prime(length)
    
    n = p * q
    phi = (p - 1) * (q - 1)

    e = 2
    while e < phi:
        if math.gcd(e, phi) == 1:
            break
        else:
            e += 1

    d = pow(e, -1, phi)

    return {"public_key": (e, n), "private_key": (d, n)}


if __name__ == '__main__':
    print(generate_rsa(1024))
