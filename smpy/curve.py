# -*- coding: utf-8 -*-
from .utils import cmp, sign, mod_inverse


class Curve(object):

    def __init__(self, ecc_table, name, bit_size):
        self.P = int(ecc_table["p"], 16)
        self.A = int(ecc_table["a"], 16)
        self.B = int(ecc_table["b"], 16)
        self.N = int(ecc_table["n"], 16)
        self.GX = int(ecc_table["gx"], 16)
        self.GY = int(ecc_table["gy"], 16)
        self.name = name
        self.bit_size = bit_size

    def double_jacobian(self, x, y, z: int):
        # See https: // hyperelliptic.org / EFD / g1p / auto - shortw - jacobian - 3.html
        # doubling-dbl-2001-b
        delta = z * z
        delta = delta % self.P
        gamma = y * y
        gamma = gamma % self.P
        alpha = x - delta
        if sign(alpha) == -1:
            alpha = alpha + self.P
        alpha2 = x + delta
        alpha = alpha * alpha2
        alpha2 = alpha
        alpha = alpha << 1
        alpha = alpha + alpha2

        alpha2 = x * gamma
        beta = alpha2

        x3 = alpha * alpha
        beta8 = beta << 3
        beta8 = beta8 % self.P
        x3 = x3 - beta8
        if sign(x3) == -1:
            x3 = x3 + self.P
        x3 = x3 % self.P

        z3 = y + z
        z3 = z3 * z3
        z3 = z3 - gamma
        if sign(z3) == -1:
            z3 = z3 + self.P
        z3 = z3 - delta
        if sign(z3) == -1:
            z3 = z3 + self.P
        z3 = z3 % self.P

        beta = beta << 2
        beta = beta - x3
        if sign(beta) == -1:
            beta = beta + self.P

        alpha = alpha * beta
        y3 = alpha

        gamma = gamma * gamma
        gamma = gamma << 3
        gamma = gamma % self.P

        y3 = y3 - gamma
        if sign(y3) == -1:
            y3 = y3 + self.P
        y3 = y3 % self.P

        return x3, y3, z3

    def add_jacobian(self, x1, y1, z1, x2, y2, z2: int):
        # See https: // hyperelliptic.org / EFD / g1p / auto - shortw - jacobian - 3.html
        # addition-add-2007-bl
        if sign(z1) == 0:
            x3 = x2
            y3 = y2
            z3 = z2
            return x3, y3, z3
        if sign(z2) == 0:
            x3 = x1
            y3 = y1
            z3 = z1
            return x3, y3, z3

        z1z1 = z1 * z1
        z1z1 = z1z1 % self.P
        z2z2 = z2 * z2
        z2z2 = z2z2 % self.P

        u1 = x1 * z2z2
        u1 = u1 % self.P
        u2 = x2 * z1z1
        u2 = u2 % self.P
        h = (u2 - u1)
        x_equal = sign(h) == 0
        if sign(h) == -1:
            h = h + self.P
        i = h << 1
        i = i * i
        j = h * i

        s1 = y1 * z2
        s1 = s1 * z2z2
        s1 = s1 % self.P
        s2 = y2 * z1
        s2 = s2 * z1z1
        s2 = s2 % self.P
        r = (s2 - s1)
        if sign(r) == -1:
            r += self.P
        y_equal = sign(r) == 0
        if x_equal and y_equal:
            return self.double_jacobian(x1, y1, z1)
        r = r << 1
        v = u1 * i

        x3 = r
        x3 *= x3
        x3 = (x3 - j)
        x3 = (x3 - v)
        x3 = (x3 - v)
        x3 = x3 % self.P

        y3 = r
        v = (v - x3)
        y3 *= v
        s1 *= j
        s1 <<= 1
        y3 = (y3 - s1)
        y3 = y3 % self.P

        z3 = z1 + z2
        z3 = z3 * z3
        z3 = (z3 - z1z1)
        z3 = (z3 - z2z2)
        z3 = z3 * h
        z3 = z3 % self.P

        return x3, y3, z3

    def affine_from_jacobian(self, x, y, z: int):
        if sign(z) == 0:
            return 0, 0

        zinv = mod_inverse(z, self.P)
        zinvsq = zinv * zinv

        x_out = x * zinvsq
        x_out = x_out % self.P
        zinvsq = zinvsq * zinv
        y_out = y * zinvsq
        y_out = y_out % self.P
        return x_out, y_out

    def matchesSpecificCurve(self,  *args):
        for c in args:
            if self == c.Params():
                return c, True
        return None, False

    def marshal(self, x, y: int):
        byte_len = (self.bit_size + 7) // 8
        ret = bytearray()
        ret.append(4)
        ret += int(x).to_bytes(byte_len, "big")
        ret += int(y).to_bytes(byte_len, "big")
        # for i in range(1, 1 + byte_len):
        #     ret.append(0)
        #     int(x).to_bytes(32, "big")
        #     write_bytes(x, ret)
        # for i in range(1 + byte_len, 1 + 2 * byte_len):
        #     ret.append(0)
        #     write_bytes(y, ret)
        return ret

    def unmarshal(self, data):
        byte_len = (self.bit_size + 7) // 8
        if len(data) != 1 + 2 * byte_len:
            return None, None
        if data[0] != 4:
            return None, None
        x = int.from_bytes(data[1: 1 + byte_len], byteorder='big')
        y = int.from_bytes(data[1 + byte_len:], byteorder='big')
        if cmp(x, self.P) > 0 or cmp(y, self.P) > 0:
            return None, None
        if not self.is_on_curve(x, y):
            return None, None
        return x, y

    def scalar_mult(self, b_x, b_y: int, k: bytes):
        # If there is a dedicated constant - time implementation for this curve operation,
        # use that instead of the generic one.
        # specific, ok = self.matchesSpecificCurve(p224, p256, p384, p521)
        # if ok:
        #     return specific.ScalarMult(b_x, b_y, k)
        b_z = 1
        x, y, z = 0, 0, 0
        for byte in k:
            # print(byte)
            for byte_num in range(8):
                x, y, z = self.double_jacobian(x, y, z)
                if byte & 0x80 == 0x80:
                    x, y, z = self.add_jacobian(b_x, b_y, b_z, x, y, z)
                byte <<= 1

        return self.affine_from_jacobian(x, y, z)

    def scalar_base_mult(self, k: bytes):
        # if specific, ok:= matchesSpecificCurve(curve, p224, p256, p384, p521)
        #     return specific.ScalarBaseMult(k)
        return self.scalar_mult(self.GX, self.GY, k)

    def is_on_curve(self, x, y):
        # If there is a dedicated constant-time implementation for this curve operation,
        # use that instead of the generic one.
        # if specific, ok := matchesSpecificCurve(curve, p224, p384, p521);
        if sign(x) < 0 or cmp(x, self.P) >= 0 or sign(y) < 0 or cmp(y, self.P) >= 0:
            return False
        # y² = x³ - 3x + b
        y2 = y * y
        y2 = y2 % self.P
        return cmp(self.polynomial(x), y2) == 0

    def polynomial(self, x):
        """returns x³ - 3x + b"""
        x3 = x * x
        x3 = x3 * x

        three_x = x << 1
        three_x = three_x + x

        x3 = (x3 - three_x + self.B) % self.P
        return x3
