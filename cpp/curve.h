//
// Created by admin on 2022/6/7.
//

#ifndef SM_CURVE_H
#define SM_CURVE_H
#include <map>
#include "bytes.h"
using std::map;

class Curve
{
public:
    Curve(map<string, string>, string, int);
public:
    uint64_t P;
    uint64_t N;
    uint64_t B;
    uint64_t GX;
    uint64_t GY;
    int bitSize;
    string name;
};
#endif //SM_CURVE_H
