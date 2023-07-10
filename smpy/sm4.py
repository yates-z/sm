import ctypes
from enum import Enum
from .utils import uint32, put_unit32, PKCS5_padding, PKCS5_unpadding

s_box = [
    0xd6, 0x90, 0xe9, 0xfe, 0xcc, 0xe1, 0x3d, 0xb7,
    0x16, 0xb6, 0x14, 0xc2, 0x28, 0xfb, 0x2c, 0x05,
    0x2b, 0x67, 0x9a, 0x76, 0x2a, 0xbe, 0x04, 0xc3,
    0xaa, 0x44, 0x13, 0x26, 0x49, 0x86, 0x06, 0x99,
    0x9c, 0x42, 0x50, 0xf4, 0x91, 0xef, 0x98, 0x7a,
    0x33, 0x54, 0x0b, 0x43, 0xed, 0xcf, 0xac, 0x62,
    0xe4, 0xb3, 0x1c, 0xa9, 0xc9, 0x08, 0xe8, 0x95,
    0x80, 0xdf, 0x94, 0xfa, 0x75, 0x8f, 0x3f, 0xa6,
    0x47, 0x07, 0xa7, 0xfc, 0xf3, 0x73, 0x17, 0xba,
    0x83, 0x59, 0x3c, 0x19, 0xe6, 0x85, 0x4f, 0xa8,
    0x68, 0x6b, 0x81, 0xb2, 0x71, 0x64, 0xda, 0x8b,
    0xf8, 0xeb, 0x0f, 0x4b, 0x70, 0x56, 0x9d, 0x35,
    0x1e, 0x24, 0x0e, 0x5e, 0x63, 0x58, 0xd1, 0xa2,
    0x25, 0x22, 0x7c, 0x3b, 0x01, 0x21, 0x78, 0x87,
    0xd4, 0x00, 0x46, 0x57, 0x9f, 0xd3, 0x27, 0x52,
    0x4c, 0x36, 0x02, 0xe7, 0xa0, 0xc4, 0xc8, 0x9e,
    0xea, 0xbf, 0x8a, 0xd2, 0x40, 0xc7, 0x38, 0xb5,
    0xa3, 0xf7, 0xf2, 0xce, 0xf9, 0x61, 0x15, 0xa1,
    0xe0, 0xae, 0x5d, 0xa4, 0x9b, 0x34, 0x1a, 0x55,
    0xad, 0x93, 0x32, 0x30, 0xf5, 0x8c, 0xb1, 0xe3,
    0x1d, 0xf6, 0xe2, 0x2e, 0x82, 0x66, 0xca, 0x60,
    0xc0, 0x29, 0x23, 0xab, 0x0d, 0x53, 0x4e, 0x6f,
    0xd5, 0xdb, 0x37, 0x45, 0xde, 0xfd, 0x8e, 0x2f,
    0x03, 0xff, 0x6a, 0x72, 0x6d, 0x6c, 0x5b, 0x51,
    0x8d, 0x1b, 0xaf, 0x92, 0xbb, 0xdd, 0xbc, 0x7f,
    0x11, 0xd9, 0x5c, 0x41, 0x1f, 0x10, 0x5a, 0xd8,
    0x0a, 0xc1, 0x31, 0x88, 0xa5, 0xcd, 0x7b, 0xbd,
    0x2d, 0x74, 0xd0, 0x12, 0xb8, 0xe5, 0xb4, 0xb0,
    0x89, 0x69, 0x97, 0x4a, 0x0c, 0x96, 0x77, 0x7e,
    0x65, 0xb9, 0xf1, 0x09, 0xc5, 0x6e, 0xc6, 0x84,
    0x18, 0xf0, 0x7d, 0xec, 0x3a, 0xdc, 0x4d, 0x20,
    0x79, 0xee, 0x5f, 0x3e, 0xd7, 0xcb, 0x39, 0x48,
]

ck = [
    0x00070e15, 0x1c232a31, 0x383f464d, 0x545b6269,
    0x70777e85, 0x8c939aa1, 0xa8afb6bd, 0xc4cbd2d9,
    0xe0e7eef5, 0xfc030a11, 0x181f262d, 0x343b4249,
    0x50575e65, 0x6c737a81, 0x888f969d, 0xa4abb2b9,
    0xc0c7ced5, 0xdce3eaf1, 0xf8ff060d, 0x141b2229,
    0x30373e45, 0x4c535a61, 0x686f767d, 0x848b9299,
    0xa0a7aeb5, 0xbcc3cad1, 0xd8dfe6ed, 0xf4fb0209,
    0x10171e25, 0x2c333a41, 0x484f565d, 0x646b7279,
]

fk = [0xa3b1bac6, 0x56aa3350, 0x677d9197, 0xb27022dc]

rotate_left32 = lambda x, k: ctypes.c_uint32(x << (k & 31) | x >> (32 - (k & 31))).value

l = lambda b: ctypes.c_uint32(
    b ^ rotate_left32(b, 2) ^ rotate_left32(b, 10) ^ rotate_left32(b, 18) ^ rotate_left32(b, 24)).value


def tau(a):
    a_arr = bytes()
    b_arr = bytearray()
    a_arr = put_unit32(a_arr, a)
    b_arr.append(s_box[a_arr[0]])
    b_arr.append(s_box[a_arr[1]])
    b_arr.append(s_box[a_arr[2]])
    b_arr.append(s_box[a_arr[3]])
    return uint32(b_arr)


t = lambda z: l(tau(z))


def r(a):
    a[0] = a[0] ^ a[3]
    a[3] = a[0] ^ a[3]
    a[0] = a[0] ^ a[3]
    a[1] = a[1] ^ a[2]
    a[2] = a[1] ^ a[2]
    a[1] = a[1] ^ a[2]


f0 = lambda x, rk: ctypes.c_uint32(x[0] ^ t(x[1] ^ x[2] ^ x[3] ^ rk)).value
f1 = lambda x, rk: ctypes.c_uint32(x[1] ^ t(x[2] ^ x[3] ^ x[0] ^ rk)).value
f2 = lambda x, rk: ctypes.c_uint32(x[2] ^ t(x[3] ^ x[0] ^ x[1] ^ rk)).value
f3 = lambda x, rk: ctypes.c_uint32(x[3] ^ t(x[0] ^ x[1] ^ x[2] ^ rk)).value


class SM4(object):

    class Mode(Enum):
        ECB = 0,
        CBC = 1

    def __init__(self, key: bytes, mode=Mode.ECB, iv=b"0"*16):
        self.__block_size = 16
        self.__key_size = 16
        self.mode = mode
        self.iv = iv

        if self.mode == self.Mode.CBC:
            if len(self.iv) < self.__block_size:
                self.iv = PKCS5_padding(iv, self.__block_size)
            elif len(self.iv) > self.__block_size:
                self.iv = self.iv[:self.__block_size]

        self.key = key
        if len(key) < self.__key_size:
            self.key = PKCS5_padding(key, self.__key_size)
        elif len(key) > self.__key_size:
            self.key = self.key[:self.__key_size]
        self.enc = self.expand_key(self.key, True)
        self.dec = self.expand_key(self.key, False)

    def expand_key(self, key, force_enc):
        mk = [
            uint32(key[:4]),
            uint32(key[4:8]),
            uint32(key[8:12]),
            uint32(key[12:16]),
        ]

        x = [mk[0] ^ fk[0], mk[1] ^ fk[1], mk[2] ^ fk[2], mk[3] ^ fk[3], 0]
        rk = [0] * 32
        if force_enc:
            for i in range(32):
                x[(i + 4) % 5] = self.enc_round(x[i % 5], x[(i + 1) % 5], x[(i + 2) % 5], x[(i + 3) % 5],
                                                x[(i + 4) % 5], rk, i)
        else:
            for i in range(32):
                x[(i + 4) % 5] = self.dec_round(x[i % 5], x[(i + 1) % 5], x[(i + 2) % 5], x[(i + 3) % 5],
                                                x[(i + 4) % 5], rk, i)

        return rk

    def lAp(self, b):
        return b ^ rotate_left32(b, 13) ^ rotate_left32(b, 23)

    def tAp(self, z):
        return self.lAp(tau(z))

    def enc_round(self, x0, x1, x2, x3, x4, rk, i):
        x4 = x0 ^ self.tAp(x1 ^ x2 ^ x3 ^ ck[i])
        rk[i] = x4
        return x4

    def dec_round(self, x0, x1, x2, x3, x4, rk, i):
        x4 = x0 ^ self.tAp(x1 ^ x2 ^ x3 ^ ck[i])
        rk[31 - i] = x4
        return x4

    def block_size(self):
        return self.__block_size

    def process_block(self, rk, src):
        x = [
            uint32(src[0: 4]),
            uint32(src[4: 8]),
            uint32(src[8: 12]),
            uint32(src[12: 16]),
        ]
        for i in range(0, 32, 4):
            x[0] = f0(x, rk[i])
            x[1] = f1(x, rk[i + 1])
            x[2] = f2(x, rk[i + 2])
            x[3] = f3(x, rk[i + 3])
        r(x)
        dst = bytes()
        dst = put_unit32(dst, x[0])
        dst = put_unit32(dst, x[1])
        dst = put_unit32(dst, x[2])
        dst = put_unit32(dst, x[3])
        return dst

    def xor_bytes(self, a, b):
        data = bytearray()
        for i in range(self.block_size()):
            data.append(a[i] ^ b[i])
        return data

    def ecb_encrypt(self, plain_text: bytes) -> (str, str):
        cipher_text = bytes()
        for i in range(0, len(plain_text), self.block_size()):
            src = plain_text[i: i + self.block_size()]
            if len(src) < self.block_size():
                raise Exception("sm4: input not full block")
            cipher_text += self.process_block(self.enc, src)
        return cipher_text.hex(), ""

    def cbc_encrypt(self, plain_text: bytes) -> (str, str):
        """
        CBC比ECB多引入了初始向量IV，先使用IV与明文异或运算,
        IV长度应与block size一致，即16字节
        """
        iv = self.iv
        tmp = bytearray()
        cipher_text = bytes()
        for i in range(len(plain_text)):
            tmp.append(0)
        while len(plain_text) > 0:
            # Write the xor to dst, then encrypt in place.
            tmp[:self.block_size()] = self.xor_bytes(plain_text[:self.block_size()], iv)
            tmp[:self.block_size()] = self.process_block(self.enc, tmp[:self.block_size()])

            # Move to the next block with this block as the next iv.
            iv = tmp[:self.block_size()]
            plain_text = plain_text[self.block_size():]
            cipher_text += tmp[:self.block_size()]
            tmp = tmp[self.block_size():]
        return cipher_text.hex(), ""

    def cbc_decrypt(self, cipher_text: bytes) -> (str, str):
        end = len(cipher_text)
        start = end - self.block_size()
        prev = start - self.block_size()
        plain_text = bytearray()
        for i in range(len(cipher_text)):
            plain_text.append(0)
        while start > 0:
            plain_text[start:end] = self.process_block(self.dec, cipher_text[start:end])
            plain_text[start:end] = self.xor_bytes(plain_text[start:end], cipher_text[prev:start])
            end = start
            start = prev
            prev -= self.block_size()
        plain_text[start:end] = self.process_block(self.dec, cipher_text[start:end])
        plain_text[start:end] = self.xor_bytes(plain_text[start:end], self.iv)
        return bytes(plain_text), ""

    def ecb_decrypt(self, cipher_text: bytes):
        if len(cipher_text) % self.block_size() != 0:
            return "", "input not full blocks"
        plain_text = bytes()
        for i in range(0, len(cipher_text), self.block_size()):
            src = cipher_text[i: i + self.block_size()]
            if len(src) < self.block_size():
                raise Exception("sm4: input not full block")
            plain_text += self.process_block(self.dec, src)
        return plain_text, ""

    def encrypt(self, plain_text: str) -> (str, str):
        """待加密的字符串长度必须是16的整数倍"""
        plain_text = plain_text.encode()
        plain_text_with_padding = PKCS5_padding(plain_text, self.block_size())
        if len(plain_text_with_padding) % self.block_size() != 0:
            return "", "input not full blocks"
        if self.mode == self.Mode.ECB:
            return self.ecb_encrypt(plain_text_with_padding)
        elif self.mode == self.Mode.CBC:
            return self.cbc_encrypt(plain_text_with_padding)

    def decrypt(self, cipher_text) -> (str, str):
        if isinstance(cipher_text, str):
            cipher_text = bytes.fromhex(cipher_text)

        if self.mode == self.Mode.ECB:
            plain_text, err = self.ecb_decrypt(cipher_text)
        elif self.mode == self.Mode.CBC:
            plain_text, err = self.cbc_decrypt(cipher_text)
        else:
            return "", "invalid mode"
        plain_text = PKCS5_unpadding(plain_text)
        return plain_text.decode(), err



