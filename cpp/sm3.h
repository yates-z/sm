//
// Created by admin on 2022/6/6.
//

#ifndef CPP_SM3_H
#define CPP_SM3_H

#include <iostream>
#include "bytes.h"


class SM3
{
public:
    SM3();
    void reset();
    int write(bytes);
    int size();
    int blockSize();
    bytes sum(bytes);
    void finish();
    void processWord(bytes, int32_t);
    void processLength(int64_t);
    void processBlock();
public:
    static const int _digestLength = 32;
    static const int _blockSize = 16;
    static const uint32_t gT[64];
private:
    uint32_t v[_digestLength/4];
    uint32_t inWords[_blockSize];
    int32_t xOff;
    uint32_t w[68];
    bytes xBuf;
    int32_t xBufOff;
    int64_t byteCount;
};
#endif //CPP_SM3_H
