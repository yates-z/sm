//
// Created by admin on 2022/6/7.
//
#include "curve.h"
#include "bigInt.h"
#include <iostream>

Curve::Curve(map <string, string> eccTable, string name, int bitSize) {

    this->name = name;
    this->bitSize = bitSize;
}


int main(){
    string p = "FFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFF";
    BigInt a(p, 16);
    BigInt b = 1000000;
    BigInt c = 1;
    std::cout << a.hex() << std::endl;
//    std::cout << a + 1 << std::endl;
//    std::cout << c  << std::endl;
    return 0;
}