//
// Created by admin on 2022/6/16.
//

#include "bigInt.h"


BigInt::BigInt(long long x)
        : neg(x < 0), _base(16) {
    if (x < 0)
        x = -x;
    while (x > 0){
        nums.push_front(x % (base() * base()));
        x = x / base() / base();
    }
}

BigInt::BigInt(string s, int base)
        : neg(s[0] == '-'), _base(base) {
    int size = s.length();
    int symbol = 0;
    if (s[0] == '-' || s[0] == '+') {
        symbol = 1;
    }
    for (int i = (size - 1); i >= symbol; i = i - 2) {
        // 低四位
        int n = hexToInt(s[i]);
        // 高四位
        if (i > 0)
            n += (hexToInt(s[i - 1]) * base);
        nums.push_front(n);
    }
}


unsigned long long BigInt::length() const {
    return nums.size();
}

int BigInt::base() const {
    return _base;
}


nat BigInt::to_bits() {
    return nums;
}

BigInt *BigInt::abs() {
    neg = false;
    return this;
}

string BigInt::hex() {
    std::vector<int> res;
    res.push_back(0);

    for (auto num : nums){
        for (auto &j : res)
            j *= base() * base();

        res[0] += int(num);

        for (int k = 0; k < res.size() - 1; k++) {
            res[k + 1] += res[k] / 16;
            res[k] = res[k] % 16;
        }

        while (res.back() >= 16) {
            res.push_back(res.back() / 16);
            res[res.size() - 2] = res[res.size() - 2] % 16;
        }
    }
//    if (neg)
//        out << "-";
    string s;
    for (auto it = res.rbegin(); it != res.rend(); ++it)
        s += intToHex(*it);
    return s;
}


BigInt BigInt::operator+(const BigInt& x) const {
    BigInt i = *this;
    i += x;
    return i;
}

BigInt& BigInt::operator+=(const BigInt& x) {
    // :todo if i less than 0

    auto it1 = nums.rbegin();
    auto it2 = x.nums.rbegin();

    int carry = 0;
    while (it1 != nums.rend() || it2 != x.nums.rend()){
        int sum = carry;

        if (it2 != x.nums.rend()){
            sum += int(*it2);
            ++ it2;
        }

        if (it1 != nums.rend()){
            sum += int(*it1);
            *it1 = sum % (base() * base());
            ++ it1;
        } else {
            nums.push_front(uint8_t(sum % (base() * base())));
            it1 = nums.rend();
        }

        carry = sum / base() / base();

    }
    if (carry)
        nums.push_front(uint8_t(carry));
    return *this;
}

BigInt BigInt::operator+(const long long& x) const {
    BigInt i = *this;
    i += x;
    return i;
}

BigInt& BigInt::operator+=(const long long& x) {
    BigInt i = x;
    return *this += i;
}

// 相当于将256进制的数转换为10进制
std::ostream &operator<<(std::ostream &out, BigInt const &a) {
    std::vector<int> res;
    res.push_back(0);
    for (auto num: a.nums) {
        for (auto &j : res)
            j *= a.base() * a.base();

        res[0] += int(num);

        for (int k = 0; k < res.size() - 1; k++) {
            res[k + 1] += res[k] / 10;
            res[k] = res[k] % 10;
        }

        while (res.back() >= 10) {
            res.push_back(res.back() / 10);
            res[res.size() - 2] = res[res.size() - 2] % 10;
        }
    }

    if (a.neg)
        out << "-";

    for (auto it = res.rbegin(); it != res.rend(); ++it)
        out << *it;
    return out;
}


int BigInt::hexToInt(char s) {
    int num = 0;
    if (s >= '0' && s <= '9')
        num += s - '0';
    else if (s >= 'a' && s <= 'f')
        num += s - 'a' + 10;
    else if (s >= 'A' && s <= 'F')
        num += s - 'A' + 10;
    return num;
}

char BigInt::intToHex(int i) {
    switch (i){
        case 0:
            return '0';
        case 1:
            return '1';
        case 2:
            return '2';
        case 3:
            return '3';
        case 4:
            return '4';
        case 5:
            return '5';
        case 6:
            return '6';
        case 7:
            return '7';
        case 8:
            return '8';
        case 9:
            return '9';
        case 10:
            return 'A';
        case 11:
            return 'B';
        case 12:
            return 'C';
        case 13:
            return 'D';
        case 14:
            return 'E';
        case 15:
            return 'F';
        default:
            return '0';
    }
}