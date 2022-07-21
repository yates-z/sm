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
    BigInt a("8", 16);
    BigInt b("-4", 16);
    BigInt c = 1;
    std::cout << a/b << " " << a <<" "<< b<< std::endl;
//    std::cout << a + 1 << std::endl;
//    std::cout << c  << std::endl;
    return 0;
}