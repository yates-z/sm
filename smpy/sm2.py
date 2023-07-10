# -*- coding: utf-8 -*-
import ctypes
import random
from enum import Enum

from .sm3 import SM3
from .curve import Curve
from .utils import is_ec_point_infinity, cmp


# 选择素域，设置椭圆曲线参数
default_ecc_table = {
    'p': 'FFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFF',
    'a': 'FFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFC',
    'b': '28E9FA9E9D9F5E344D5A9E4BCF6509A7F39789F515AB8F92DDBCBD414D940E93',
    'n': 'FFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFF7203DF6B21C6052B53BBF40939D54123',
    'gx': '32C4AE2C1F1981195F9904466A39C9948FE30BBFF2660BE1715A4589334C74C7',
    'gy': 'BC3736A2F4F6779C59BDCEE36B692153D0A9877CC62A474002DF32E52139F0A0'
}


class SM2(object):

    class TextType(Enum):
        C1C2C3 = 0
        C1C3C2 = 1

    bit_size = 256
    key_bytes = (bit_size + 7) // 8
    sm2H = 1
    curve = Curve(default_ecc_table, "SM2-P-256-V1", 256)

    def __init__(self, private_key=None, public_key=None, mode=TextType.C1C2C3):
        self.private_key = private_key

        self.pub_x = bytes()
        self.pub_y = bytes()
        if public_key:
            self.public_key = bytes.fromhex(public_key)
            self.pub_x = int.from_bytes(self.public_key[: len(self.public_key)//2], "big")
            self.pub_y = int.from_bytes(self.public_key[len(self.public_key)//2:], "big")

        self.mode = mode

    @classmethod
    def generate_key(cls):
        bit_len = (cls.bit_size + 7) // 8
        priv = bytearray()
        # test_arr = [26, 161, 81, 63, 56, 18, 13, 215, 144, 49, 106, 107, 43, 91, 67, 174, 112, 143, 119, 126, 71, 147,
        #             196, 78, 187, 254, 46, 185, 8, 72, 106, 61]
        # for i in test_arr:
        #     priv.append(i)
        for i in range(bit_len):
            priv.append(random.randint(0, 255))
        x, y = None, None
        mask = [0xff, 0x1, 0x3, 0x7, 0xf, 0x1f, 0x3f, 0x7f]
        while x is None:
            priv[0] &= mask[cls.bit_size % 8]

            priv[1] ^= 0x42
            priv_int = int.from_bytes(bytes(priv), "big")
            if cmp(priv_int, cls.curve.N) >= 0:
                continue
            x, y = cls.curve.scalar_base_mult(bytes(priv))
        x_bytes = x.to_bytes(32, "big")
        # x_bytes = bytearray(x_bytes)
        y_bytes = y.to_bytes(32, "big")
        pub = bytearray()
        for _ in range(1 + 2 * cls.key_bytes):
            pub.append(0)
        pub[0] = 0x04
        if len(x_bytes) > cls.key_bytes:
            pub[1: 1 + cls.key_bytes] = x_bytes[len(x_bytes)-cls.key_bytes:]
        elif len(x_bytes) < cls.key_bytes:
            pub[1 + (cls.key_bytes - len(x_bytes)):1 + cls.key_bytes] = x_bytes
        else:
            pub[1: 1 + cls.key_bytes] = x_bytes

        if len(y_bytes) > cls.key_bytes:
            pub[1 + cls.key_bytes:] = y_bytes[len(y_bytes)-cls.key_bytes:]
        elif len(y_bytes) < cls.key_bytes:
            pub[1 + cls.key_bytes + (cls.key_bytes - len(y_bytes)):] = y_bytes
        else:
            pub[1 + cls.key_bytes:] = y_bytes

        if len(priv) > cls.key_bytes:
            raw = priv[len(priv) - cls.key_bytes:]
        elif len(priv) < cls.key_bytes:
            raw = bytearray()
            for i in range(cls.key_bytes):
                raw.append(0)
            raw[cls.key_bytes - len(priv):] = priv
        else:
            raw = priv
        return bytes(raw), pub[1:]

    def xor(self, data, kdf_out, d_remaining_int):
        for i in range(d_remaining_int):
            data[i] ^= kdf_out[i]
        # print("xor", data.hex())
        return data

    def new_bytes(self, size):
        b = bytearray()
        for _ in range(size):
            b.append(0)
        return b

    @staticmethod
    def put_unit32(b, v):
        _ = b[3]
        b[0] = ctypes.c_uint8((v >> 24)).value
        b[1] = ctypes.c_uint8((v >> 16)).value
        b[2] = ctypes.c_uint8((v >> 8)).value
        b[3] = ctypes.c_uint8(v).value
        return b

    def kdf(self, digest, c1x: int, c1y: int, enc_data):
        buf_size = 4
        if buf_size < digest.size():
            buf_size = digest.size()
        buf = self.new_bytes(buf_size)
        enc_data_len = len(enc_data)
        c1x_bytes = c1x.to_bytes(32, byteorder="big")
        c1y_bytes = c1y.to_bytes(32, byteorder="big")
        off = 0
        count = 0
        while off < enc_data_len:
            digest.reset()
            digest.write(c1x_bytes)
            digest.write(c1y_bytes)
            count += 1
            buf = self.put_unit32(buf, ctypes.c_uint32(count).value)
            digest.write(buf[:4])
            tmp = digest.sum(bytes())
            for i in range(buf_size):
                if i < len(buf):
                    buf[i] = tmp[i]
                else:
                    buf.append(tmp[i])
            xor_len = enc_data_len - off
            if xor_len > digest.size():
                xor_len = digest.size()
            enc_data = enc_data[:off] + self.xor(enc_data[off:], buf, xor_len)
            off += xor_len
        return enc_data

    def next_k(self, max_num):
        min_num = 1
        while True:
            k = random.randint(min_num, max_num)
            if cmp(k, min_num) >= 0:
                return k

    def not_encrypted(self, enc_data, data: bytes):
        enc_data_len = len(enc_data)
        for i in range(enc_data_len):
            if enc_data[i] != data[i]:
                return False
        return True

    def encrypt(self, data: str):
        if not isinstance(data, str) or len(data) == 0:
            return None, "invalid cipher text: length == 0 or not str"
        data = data.encode()
        c2 = bytearray(data)
        digest = SM3()
        while True:
            k = self.next_k(self.curve.N)
            k_bytes = int(k).to_bytes(32, "big")
            c1x, c1y = self.curve.scalar_base_mult(k_bytes)
            c1 = self.curve.marshal(c1x, c1y)
            kPBx, kPBy = self.curve.scalar_mult(self.pub_x, self.pub_y, k_bytes)
            c2 = self.kdf(digest, kPBx, kPBy, c2)
            if not self.not_encrypted(c2, data):
                break
        digest.reset()
        digest.write(kPBx.to_bytes(32, byteorder="big"))
        digest.write(data)
        digest.write(kPBy.to_bytes(32, byteorder="big"))
        c3 = digest.sum(bytes())

        result = bytes()
        if self.mode == self.TextType.C1C2C3:
            result += c1
            result += c2
            result += c3
        elif self.mode == self.TextType.C1C3C2:
            result += c1
            result += c3
            result += c2
        else:
            return None, "unknown cipherTextType"
        return result, None

    def decrypt(self, data: bytes):
        data = bytearray(data)
        c1_len = ((self.bit_size + 7) >> 3) * 2 + 1
        c1 = data[: c1_len]
        c1x, c1y = self.curve.unmarshal(c1)
        sx, sy = self.curve.scalar_mult(c1x, c1y, self.sm2H.to_bytes(1, byteorder="big"))
        if is_ec_point_infinity(sx, sy):
            return None, "[h]C1 at infinity"
        c1x, c1y = self.curve.scalar_mult(c1x, c1y, bytes.fromhex(self.private_key))

        digest = SM3()
        c3_len = digest.size()
        c2_len = len(data) - c1_len - c3_len
        if self.mode == self.TextType.C1C2C3:
            c2 = data[c1_len: c1_len + c2_len]
            c3 = data[c1_len + c2_len:]
        elif self.mode == self.TextType.C1C3C2:
            c3 = data[c1_len: c1_len + c3_len]
            c2 = data[c1_len + c3_len]
        else:
            return None, "unknown cipherTextType: {}".format(self.mode)
        c2 = self.kdf(digest, c1x, c1y, c2)
        digest.reset()
        digest.write(c1x.to_bytes(32, byteorder="big"))
        digest.write(c2)
        digest.write(c1y.to_bytes(32, byteorder="big"))
        new_c3 = digest.sum(bytes())
        if not str(new_c3) == str(c3):
            return None, "invalid cipher text"
        return bytes(c2), None


