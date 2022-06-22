//
// Created by admin on 2022/6/6.
//
#include "sm3.h"

uint32_t rotateLeft32(uint32_t x, uint32_t k)
{
    const uint32_t n = 32;
    uint32_t s = uint8_t(k) & (n - 1);
    return x<<s | x>>(n-s);
}

uint32_t p0(uint32_t x)
{
    uint32_t r9 = rotateLeft32(x, 9);
    uint32_t r17 = rotateLeft32(x, 17);
    return x ^ r9 ^ r17;
}

uint32_t p1(uint32_t x)
{
    uint32_t r15 = rotateLeft32(x, 15);
    uint32_t r23 = rotateLeft32(x, 23);
    return x ^ r15 ^ r23;
}

uint32_t ff0(uint32_t x, uint32_t y, uint32_t z)
{
    return x ^ y ^ z;
}

uint32_t ff1(uint32_t x, uint32_t y, uint32_t z) {
    return (x & y) | (x & z) | (y & z);
}

uint32_t gg0(uint32_t x, uint32_t y, uint32_t z)
{
    return x ^ y ^ z;
}

uint32_t gg1(uint32_t x , uint32_t y, uint32_t z) {
    return (x & y) | ((~x) & z);
}

const uint32_t SM3::gT[64] = {
        0x79CC4519, 0xF3988A32, 0xE7311465, 0xCE6228CB, 0x9CC45197, 0x3988A32F, 0x7311465E, 0xE6228CBC,
        0xCC451979, 0x988A32F3, 0x311465E7, 0x6228CBCE, 0xC451979C, 0x88A32F39, 0x11465E73, 0x228CBCE6,
        0x9D8A7A87, 0x3B14F50F, 0x7629EA1E, 0xEC53D43C, 0xD8A7A879, 0xB14F50F3, 0x629EA1E7, 0xC53D43CE,
        0x8A7A879D, 0x14F50F3B, 0x29EA1E76, 0x53D43CEC, 0xA7A879D8, 0x4F50F3B1, 0x9EA1E762, 0x3D43CEC5,
        0x7A879D8A, 0xF50F3B14, 0xEA1E7629, 0xD43CEC53, 0xA879D8A7, 0x50F3B14F, 0xA1E7629E, 0x43CEC53D,
        0x879D8A7A, 0x0F3B14F5, 0x1E7629EA, 0x3CEC53D4, 0x79D8A7A8, 0xF3B14F50, 0xE7629EA1, 0xCEC53D43,
        0x9D8A7A87, 0x3B14F50F, 0x7629EA1E, 0xEC53D43C, 0xD8A7A879, 0xB14F50F3, 0x629EA1E7, 0xC53D43CE,
        0x8A7A879D, 0x14F50F3B, 0x29EA1E76, 0x53D43CEC, 0xA7A879D8, 0x4F50F3B1, 0x9EA1E762, 0x3D43CEC5
};

SM3::SM3()
{
    reset();
}

void SM3::reset()
{
    byteCount = 0;
    xBufOff = 0;
    xBuf = {0,0,0,0};

    for (auto &i :inWords)
        i = 0;

    for (auto &i : w)
        i= 0;

    v[0] = 0x7380166F;
    v[1] = 0x4914B2B9;
    v[2] = 0x172442D7;
    v[3] = 0xDA8A0600;
    v[4] = 0xA96F30BC;
    v[5] = 0x163138AA;
    v[6] = 0xE38DEE4D;
    v[7] = 0xB0FB0E4E;

    xOff = 0;
}

int SM3::size() {
    return _digestLength;
}

int SM3::blockSize() {
    return _blockSize;
}


int SM3::write(bytes p) {
    byte _ = p[0];
    uint32_t inLen = p.size();
    uint32_t i = 0;
    if (xBufOff != 0) {
        while (i < inLen) {
                xBuf[xBufOff] = p[i];
                xBufOff++;
                i++;
                if (xBufOff == 4) {
                    processWord(xBuf, 0);
                    xBufOff = 0;
                    break;
                }
        }
    }

    uint32_t limit = ((inLen - i) & ~uint32_t(3)) + i;
    for (; i < limit; i += 4) {
        processWord(p, int32_t(i));
    }

    while( i < inLen) {
            xBuf[xBufOff] = p[i];
            xBufOff++;
            i++;
    }

    byteCount += int64_t(inLen);

    return inLen;
}

void SM3::processBlock() {
    for (int j = 0; j < 16; j++)
        w[j] = inWords[j];

    for (int j = 16; j < 68; j++) {
        uint32_t wj3= w[j-3];
        uint32_t r15 = (wj3 << uint32_t(15)) | (wj3 >> uint32_t(32 - 15));
        uint32_t wj13 = w[j-13];
        uint32_t r7 = (wj13 << uint32_t(7)) | (wj13 >> uint32_t(32 - 7));
        w[j] = p1(w[j-16]^w[j-9]^r15) ^ r7 ^ w[j-6];
    }

    uint32_t A = v[0];
    uint32_t B = v[1];
    uint32_t C = v[2];
    uint32_t D = v[3];
    uint32_t E = v[4];
    uint32_t F = v[5];
    uint32_t G = v[6];
    uint32_t H = v[7];

    for (int j = 0; j < 16; j++) {
        uint32_t a12 = (A << 12) | (A >> (32 - 12));
        uint32_t s1 = a12 + E + gT[j];
        uint32_t SS1 = (s1 << 7) | (s1 >> (32 - 7));
        uint32_t SS2 = SS1 ^ a12;
        uint32_t Wj = w[j];
        uint32_t W1j = Wj ^ w[j+4];
        uint32_t TT1 = ff0(A, B, C) + D + SS2 + W1j;
        uint32_t TT2 = gg0(E, F, G) + H + SS1 + Wj;
        D = C;
        C = (B << 9) | (B >> (32 - 9));
        B = A;
        A = TT1;
        H = G;
        G = (F << 19) | (F >> (32 - 19));
        F = E;
        E = p0(TT2);
    }

    for (int j = 16; j < 64; j++) {
        uint32_t a12 = (A << 12) | (A >> (32 - 12));
        uint32_t s1 = a12 + E + gT[j];
        uint32_t SS1 = (s1 << 7) | (s1 >> (32 - 7));
        uint32_t SS2 = SS1 ^ a12;
        uint32_t Wj = w[j];
        uint32_t W1j = Wj ^ w[j+4];
        uint32_t TT1 = ff1(A, B, C) + D + SS2 + W1j;
        uint32_t TT2 = gg1(E, F, G) + H + SS1 + Wj;
        D = C;
        C = (B << 9) | (B >> (32 - 9));
        B = A;
        A = TT1;
        H = G;
        G = (F << 19) | (F >> (32 - 19));
        F = E;
        E = p0(TT2);
    }

    v[0] ^= A;
    v[1] ^= B;
    v[2] ^= C;
    v[3] ^= D;
    v[4] ^= E;
    v[5] ^= F;
    v[6] ^= G;
    v[7] ^= H;

    xOff = 0;
}

void SM3::processWord(bytes in, int32_t inOff) {
    byte b[4];
    for (int i = inOff; i< inOff + 4; i++){
        b[i] = in[i];
    }
    uint32_t n = uint32_t(b[3]) | uint32_t(b[2])<<8 | uint32_t(b[1])<<16 | uint32_t(b[0])<<24;

    inWords[xOff] = n;
    xOff++;

    if (xOff >= 16)
        processBlock();
}

void SM3::processLength(int64_t bitLength) {
    if (xOff > (_blockSize - 2)) {
        inWords[xOff] = 0;
        xOff++;

        processBlock();
    }

    for (; xOff < (_blockSize - 2); xOff++)
        inWords[xOff] = 0;

    inWords[xOff] = uint32_t(bitLength >> 32);
    xOff++;
    inWords[xOff] = uint32_t(bitLength);
    xOff++;
}

bytes SM3::sum(bytes b) {
    finish();
    int vLen = sizeof(v) / sizeof(v[0]);
    for (int i = 0; i < vLen; i++) {
        b.push_back(byte(v[i] >> 24));
        b.push_back(byte(v[i] >> 16));
        b.push_back(byte(v[i] >> 8));
        b.push_back(byte(v[i]));
    }
    return b;
}


void SM3::finish() {
    int bitLength = byteCount << 3;
    write({128});
    while (xBufOff != 0) {
        write({0});
    }

    processLength(bitLength);

    processBlock();
}
