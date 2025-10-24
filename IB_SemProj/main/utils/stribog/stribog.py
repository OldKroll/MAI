from main.utils.stribog.const import Pi, tau, Ci, l


def XOR(A, B):
    return [a ^ b for a, b in zip(A, B)]


def plus(A, B):
    result = [0] * 64
    i, remain = 63, 0
    while i >= 0:
        s = A[i] + B[i] + remain
        remain = (s >> 8) if s >= 256 else 0
        result[i] = s & 0xFF
        i -= 1
    return result


def P(A):
    result = [0] * 64
    for i in range(0, 64):
        result[i] = A[tau[i]]

    return result


def S(A):

    result = [0] * 64
    for i in range(0, 64):
        result[i] = Pi[A[i]]

    return result


def L(A):
    result = [0] * 64
    i = 7
    while i >= 0:
        n = 0
        while n <= 7:
            p = 63
            j = 7
            while j >= 0:
                k = 0
                while k <= 7:
                    if (A[i * 8 + j] >> k) & 1:
                        result[i * 8 + n] ^= l[p * 8 + n]
                    p -= 1
                    k += 1
                j -= 1
            n += 1
        i -= 1
    return result


def X(K, A):
    return XOR(K, A)


def LPS(A):
    return L(P(S(A)))


def E(K, M):
    result = X(K, M)
    i = 0
    while i < 12:
        result = LPS(result)
        K = XOR(K, Ci[i])
        K = LPS(K)
        result = X(K, result)
        i += 1

    return result


def g(N, h, m):

    result = XOR(h, N)
    result = LPS(result)

    result = E(result, m)
    result = XOR(result, h)
    result = XOR(result, m)

    return result


def stribog_hash(string: str, hashsize: int = 256) -> str:

    h = [1 if hashsize == 256 else 0] * 64

    e = [0] * 64
    N = [0] * 64
    Z = [0] * 64
    m = [0] * 64

    start = 0
    while start + 64 <= len(string):
        for i in range(0, 64):
            m[63 - i] = ord(string[start + i])

        h = g(N, h, m)

        e[62] = 512 >> 8
        e[63] = 512 & 0xFF
        N = plus(N, e)

        Z = plus(Z, m)

        start += 64

    sz = len(string) - start
    m = [0] * 64
    for i in range(0, sz):
        m[63 - i] = ord(string[start + i])
    m[64 - sz - 1] = 1

    h = g(N, h, m)
    e[62] = (sz * 8) >> 8
    e[63] = (sz * 8) & 0xFF
    N = plus(N, e)
    Z = plus(Z, m)

    e[62] = 0
    e[63] = 0
    h = g(e, h, N)

    h = g(e, h, Z)

    return "".join(
        reversed([("%0.2X" % a) for a in h][: (32 if hashsize == 256 else 64)])
    )


if __name__ == "__main__":
    msg = "323130393837363534333231303938373635343332313039383736353433323130393837363534333231303938373635343332313039383736353433323130"
    print(stribog_hash(msg, 512))
    print("DC4B144041F9EB195E7DD254CDAA6675DAF720CE2F5FC872C4F5B8450A82605115E20B5B4ABD8BAAB8DD55C035B10435D66EA65978BD75A1F6B82208861EE7B6")
