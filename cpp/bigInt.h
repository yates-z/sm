//
// Created by admin on 2022/6/16.
//

#ifndef SM_BIGINT_H
#define SM_BIGINT_H

#include <list>
#include <vector>
#include <string>
#include <iostream>

using std::list;
using std::string;

typedef list<uint8_t> nat;

class BigInt
{
public:
    BigInt(long long);
    explicit BigInt(string s="0", int base=10);

    // Features
    int base() const;
    unsigned long long length() const;

    // Conversion func
    nat to_bits();
    BigInt* abs();
    string hex();

    // Plus
    BigInt operator+(const BigInt&) const;
    BigInt& operator+=(const BigInt&);
    BigInt operator+(const long long&) const;
    BigInt& operator+=(const long long&);

    // Subtraction :todo

    // Output
    friend std::ostream &operator<<(std::ostream &, BigInt const &);
    // Input :todo

    // static utils
    static int hexToInt(char);
    char intToHex(int);

protected:
    bool neg;
    nat nums;
private:
    int _base;
};
#endif //SM_BIGINT_H
