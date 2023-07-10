# -*- coding: utf-8 -*-
import ctypes
from .utils import uint32, put_unit32

rotate_left32 = lambda x, k: ctypes.c_uint32(x << (k & 31) | x >> (32 - (k & 31))).value


p0 = lambda x: x ^ rotate_left32(x, 9) ^ rotate_left32(x, 17)
p1 = lambda x: x ^ rotate_left32(x, 15) ^ rotate_left32(x, 23)


ff0 = lambda x, y, z: x ^ y ^ z
ff1 = lambda x, y, z: (x & y) | (x & z) | (y & z)

gg0 = lambda x, y, z: x ^ y ^ z
gg1 = lambda x, y, z: (x & y) | ((~x) & z)


class SM3(object):

    DigestLength = 32
    BlockSize = 16
    gT = [
        0x79CC4519, 0xF3988A32, 0xE7311465, 0xCE6228CB, 0x9CC45197, 0x3988A32F, 0x7311465E, 0xE6228CBC,
        0xCC451979, 0x988A32F3, 0x311465E7, 0x6228CBCE, 0xC451979C, 0x88A32F39, 0x11465E73, 0x228CBCE6,
        0x9D8A7A87, 0x3B14F50F, 0x7629EA1E, 0xEC53D43C, 0xD8A7A879, 0xB14F50F3, 0x629EA1E7, 0xC53D43CE,
        0x8A7A879D, 0x14F50F3B, 0x29EA1E76, 0x53D43CEC, 0xA7A879D8, 0x4F50F3B1, 0x9EA1E762, 0x3D43CEC5,
        0x7A879D8A, 0xF50F3B14, 0xEA1E7629, 0xD43CEC53, 0xA879D8A7, 0x50F3B14F, 0xA1E7629E, 0x43CEC53D,
        0x879D8A7A, 0x0F3B14F5, 0x1E7629EA, 0x3CEC53D4, 0x79D8A7A8, 0xF3B14F50, 0xE7629EA1, 0xCEC53D43,
        0x9D8A7A87, 0x3B14F50F, 0x7629EA1E, 0xEC53D43C, 0xD8A7A879, 0xB14F50F3, 0x629EA1E7, 0xC53D43CE,
        0x8A7A879D, 0x14F50F3B, 0x29EA1E76, 0x53D43CEC, 0xA7A879D8, 0x4F50F3B1, 0x9EA1E762, 0x3D43CEC5]

    def __init__(self):
        self.v = [0] * (self.DigestLength // 4)
        self.in_words = [0] * self.BlockSize
        self.x_off = 0
        self.w = [0] * 68
        self.x_buf = bytearray()
        self.x_buf_off = 0
        self.byte_count = 0

        self.reset()

    def reset(self):
        self.byte_count = 0
        self.x_buf_off = 0
        for i in range(len(self.x_buf) or 4):
            self.x_buf.append(0)

        for i in range(len(self.in_words)):
            self.in_words[i] = 0

        for i in range(len(self.w)):
            self.w[i] = 0

        self.v[0] = 0x7380166F
        self.v[1] = 0x4914B2B9
        self.v[2] = 0x172442D7
        self.v[3] = 0xDA8A0600
        self.v[4] = 0xA96F30BC
        self.v[5] = 0x163138AA
        self.v[6] = 0xE38DEE4D
        self.v[7] = 0xB0FB0E4E

        self.x_off = 0

    def write(self, p: bytes):
        _ = p[0]
        in_len = len(p)
        i = 0
        if self.x_buf_off != 0:
            while i < in_len:
                self.x_buf[self.x_buf_off] = p[i]
                self.x_buf_off += 1
                i += 1
                if self.x_buf_off == 4:
                    self.process_word(self.x_buf, 0)
                    self.x_buf_off = 0
                    break
        limit = ((in_len - i) & ~ 3) + i
        for _ in range(i, limit, 4):
            self.process_word(p, int(i))
            i += 4
        while i < in_len:
            self.x_buf[self.x_buf_off] = p[i]
            self.x_buf_off += 1
            i += 1
        self.byte_count += int(in_len)

        n = in_len
        return n, None

    def size(self):
        return self.DigestLength

    def sum(self, b=bytes()):
        h = self.check_sum()
        return bytearray(b + h)

    def check_sum(self):
        self.finish()
        v_len = len(self.v)
        out = bytes()
        for i in range(v_len):
            out = put_unit32(out, self.v[i])
        return out

    def finish(self):
        bit_length = self.byte_count << 3
        self.write(bytearray(int(128).to_bytes(1, "big")))
        while self.x_buf_off != 0:
            self.write(bytearray(int(0).to_bytes(1, "big")))
        self.process_length(bit_length)
        self.process_block()

    def process_word(self, _in: bytes, in_off):
        n = uint32(_in[in_off: in_off + 4])

        self.in_words[self.x_off] = ctypes.c_uint32(n).value
        self.x_off += 1
        if self.x_off >= 16:
            self.process_block()

    def process_length(self, bit_length):
        if self.x_off > (self.BlockSize - 2):
            self.in_words[self.x_off] = 0
            self.x_off += 1
            self.process_block()

        for _ in range(self.x_off, self.BlockSize - 2):
            self.in_words[self.x_off] = 0
            self.x_off += 1

        self.in_words[self.x_off] = ctypes.c_uint32(bit_length >> 32).value
        self.x_off += 1
        self.in_words[self.x_off] = ctypes.c_uint32(bit_length).value
        self.x_off += 1

    def process_block(self):
        for j in range(16):
            self.w[j] = self.in_words[j]
        for j in range(16, 68):
            wj3 = ctypes.c_uint32(self.w[j - 3]).value
            r15 = ctypes.c_uint32((wj3 << 15) | (wj3 >> (32 - 15))).value
            wj13 = ctypes.c_uint32(self.w[j - 13]).value
            r7 = ctypes.c_uint32((wj13 << 7) | (wj13 >> (32 - 7))).value
            self.w[j] = ctypes.c_uint32(p1(self.w[j - 16] ^ self.w[j - 9] ^ r15) ^ r7 ^ self.w[j - 6]).value
        A = ctypes.c_uint32(self.v[0]).value
        B = ctypes.c_uint32(self.v[1]).value
        C = ctypes.c_uint32(self.v[2]).value
        D = ctypes.c_uint32(self.v[3]).value
        E = ctypes.c_uint32(self.v[4]).value
        F = ctypes.c_uint32(self.v[5]).value
        G = ctypes.c_uint32(self.v[6]).value
        H = ctypes.c_uint32(self.v[7]).value

        for j in range(16):
            a12 = ctypes.c_uint32((A << 12) | (A >> (32 - 12))).value
            s1 = ctypes.c_uint32(a12 + E + self.gT[j]).value
            SS1 = ctypes.c_uint32((s1 << 7) | (s1 >> (32 - 7))).value
            SS2 = ctypes.c_uint32(SS1 ^ a12).value
            Wj = ctypes.c_uint32(self.w[j]).value
            W1j = ctypes.c_uint32(Wj ^ self.w[j + 4]).value
            TT1 = ctypes.c_uint32(ff0(A, B, C) + D + SS2 + W1j).value
            TT2 = ctypes.c_uint32(gg0(E, F, G) + H + SS1 + Wj).value
            D = C
            C = ctypes.c_uint32((B << 9) | (B >> (32 - 9))).value
            B = A
            A = TT1
            H = G
            G = ctypes.c_uint32((F << 19) | (F >> (32 - 19))).value
            F = E
            E = p0(TT2)
        for j in range(16, 64):
            a12 = ctypes.c_uint32((A << 12) | (A >> (32 - 12))).value
            s1 = ctypes.c_uint32(a12 + E + self.gT[j]).value
            SS1 = ctypes.c_uint32((s1 << 7) | (s1 >> (32 - 7))).value
            SS2 = ctypes.c_uint32(SS1 ^ a12).value
            Wj = ctypes.c_uint32(self.w[j]).value
            W1j = ctypes.c_uint32(Wj ^ self.w[j + 4]).value
            TT1 = ctypes.c_uint32(ff1(A, B, C) + D + SS2 + W1j).value
            TT2 = ctypes.c_uint32(gg1(E, F, G) + H + SS1 + Wj).value
            D = C
            C = ctypes.c_uint32((B << 9) | (B >> (32 - 9))).value
            B = A
            A = TT1
            H = G
            G = ctypes.c_uint32((F << 19) | (F >> (32 - 19))).value
            F = E
            E = p0(TT2)
        self.v[0] ^= A
        self.v[1] ^= B
        self.v[2] ^= C
        self.v[3] ^= D
        self.v[4] ^= E
        self.v[5] ^= F
        self.v[6] ^= G
        self.v[7] ^= H

        for index, data in enumerate(self.v):
            self.v[index] = ctypes.c_uint32(data).value

        self.x_off = 0
