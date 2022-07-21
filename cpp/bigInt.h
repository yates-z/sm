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
    explicit BigInt(string s="0", int base=16);

    // Features
    int base() const;
    unsigned long long length() const;

    // Conversion func
    nat to_bits();
    BigInt* to_abs();
    BigInt abs() const;
    string hex();

    // Plus
    BigInt operator+(const BigInt&) const;
    BigInt& operator+=(const BigInt&);
    BigInt operator+(const long long&) const;
    BigInt& operator+=(const long long&);

    // Subtraction
    BigInt operator-(const BigInt&) const;
    BigInt& operator-=(const BigInt&);

    // Multi
    BigInt operator*(const BigInt&) const;
    BigInt& operator*=(const BigInt&);

    // div
    BigInt operator/(const BigInt&) const;
    BigInt& operator/=(const BigInt&);

    // Compare
    bool operator<(const BigInt&) const;
    bool operator<=(const BigInt&) const;
    bool operator>(const BigInt&) const;
    bool operator>=(const BigInt&) const;
    bool operator==(const BigInt&) const;
    bool operator!=(const BigInt&) const;

    // Output
    friend std::ostream &operator<<(std::ostream &, BigInt const &);
    // Input :todo

    // static utils
    static int hexToInt(char);
    static char intToHex(int);

private:
    int compare(const BigInt&) const;
    std::list<uint8_t> _subtract(const std::list<uint8_t>& a, const std::list<uint8_t>& b);
    std::list<uint8_t> _multiply(const std::list<uint8_t>& a, const std::list<uint8_t>& b);

protected:
    bool neg;
    nat nums;
private:
    int _base;
};
#endif //SM_BIGINT_H
