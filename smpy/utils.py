# -*- coding: utf-8 -*-
import ctypes

def cmp(x, y):
    if x < y:
        return -1
    elif x == y:
        return 0
    else:
        return 1


def sign(x):
    if (x) == 0:
        return 0
    if x < 0:
        return -1
    else:
        return 1


def mod_inverse(a, m):
    def egcd(a, b):
        if a == 0:
            return (b, 0, 1)
        else:
            g, y, x = egcd(b % a, a)
            return (g, x - (b // a) * y, y)

    g, x, y = egcd(a, m)
    if g != 1:
        raise Exception('modular inverse does not exist')
    else:
        return x % m


def is_ec_point_infinity(x, y: int):
    if sign(x) == 0 and sign(y) == 0:
        return True
    return False


def write_bytes(x: int, buf: bytearray):
    i = len(buf)
    for index, byte in range(x):
        for j in range(8):
            i -= 1
            if i >= 0:
                buf[i] = byte
            elif byte != 0:
                raise ValueError("buffer too small to fit value")
            byte >>= 8
    if i < 0:
        i = 0
    while i < len(buf) and buf[i] == 0:
        i += 1
    return buf


def uint32(b: bytes):
    _ = b[3]
    return int(b[3]) | int(b[2]) << 8 | int(b[1]) << 16 | int(b[0]) << 24


def put_unit32(b, v):
    # _ = b[3]  # early bounds check to guarantee safety of writes below
    b += ctypes.c_uint8((v >> 24)).value.to_bytes(1, byteorder="big")
    b += ctypes.c_uint8((v >> 16)).value.to_bytes(1, byteorder="big")
    b += ctypes.c_uint8((v >> 8)).value.to_bytes(1, byteorder="big")
    b += ctypes.c_uint8(v).value.to_bytes(1, byteorder="big")
    return b


def PKCS5_padding(src: bytes, block_size):
    padding = block_size - len(src) % block_size
    for i in range(padding):
        src += int.to_bytes(padding, 1, "big")
    return src


def PKCS5_unpadding(src: bytes):
    unpadding = int.from_bytes(src[len(src)-1: len(src)], "big")
    return src[:(len(src) - unpadding)]