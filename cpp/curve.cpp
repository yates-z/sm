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
    BigInt a("-11", 10);
    BigInt b("2", 10);
//    BigInt c = a;

    std::cout <<" "<< a % b << " "<<std::endl;
//    std::cout << a + 1 << std::endl;
//    std::cout << c  << std::endl;
    return 0;
}