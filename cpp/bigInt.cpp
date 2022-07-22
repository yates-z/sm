//
// Created by admin on 2022/6/16.
//

#include "bigInt.h"


BigInt::BigInt(long long x)
        : neg(x < 0), _base(16) {
    if (x < 0)
        x = -x;
    if (x == 0)
        nums.push_back(0);
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

BigInt *BigInt::to_abs() {
    neg = false;
    return this;
}

BigInt BigInt::abs() const {
    BigInt i;
    i._base = _base;
    i.neg = false;
    i.nums = nums;
    return i;
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
    string s;
    if (neg)
        s += "-";
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

    if (neg && !x.neg){
        *this = x - *this->to_abs();
        return *this;
    } else if (!neg && x.neg) return *this -= x.abs();

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

BigInt BigInt::operator-(const BigInt& x) const {
    BigInt i = *this;
    i -= x;
    return i;
}

std::list<uint8_t> BigInt::_subtract(const std::list<uint8_t>& a, const std::list<uint8_t>& b) {
    std::list<uint8_t> new_nums = {};
    auto it1 = a.rbegin();
    auto it2 = b.rbegin();
    int diff = 0;
    while (it1 != a.rend() || it2 != b.rend()){

        if (it1 != a.rend()){
            diff += int(*it1);

            ++ it1;
        }
        if (it2 != b.rend()){
            diff -= int(*it2);
            ++it2;
        }
        if (diff < 0){
            new_nums.push_front(base() * base() + diff);
            diff = -1;
        } else {
            new_nums.push_front(diff % (base() * base()));
            diff = diff / base() / base();
        }
    }
    // 去除高位的0, 如果new_nums = {0} 则保留
    while (new_nums.size() > 1) {
        if (new_nums.front() == 0)
            new_nums.pop_front();
        else
            break;
    }
    // 最高位用1/0表示正负
    if (diff < 0){
        new_nums.front() = base() * base() - int(new_nums.front());
        new_nums.push_front(0);
    } else {
        new_nums.push_front(1);
    }
    return new_nums;
}

BigInt& BigInt::operator-=(const BigInt& x) {
    if (neg && x.neg){
        *this = x.abs() - *this->to_abs();
        return *this;
    } else if (neg && !x.neg){
        *this = *this->to_abs() + x.abs();
        neg = true;
        return *this;
    }else if (!neg && x.neg) return *this += x.abs();

    std::list<uint8_t> new_nums;

    if (length() > x.length())
        new_nums = _subtract(nums, x.nums);
    else if (length() < x.length()) {
        neg = true;
        new_nums = _subtract(x.nums, nums);
    } else {
        new_nums = _subtract(nums, x.nums);
        neg = new_nums.front() == 0;
    }
    new_nums.pop_front();
    nums = new_nums;
    return *this;
}

BigInt BigInt::operator-(const long long& x) const {
    BigInt i = *this;
    i -= x;
    return i;
}

BigInt& BigInt::operator-=(const long long& x) {
    BigInt i = x;
    return *this -= i;
}


BigInt BigInt::operator*(const BigInt& x) const {
    BigInt i = *this;
    i *= x;
    return i;
}

std::list<uint8_t> BigInt::_multiply(const std::list<uint8_t> &a, const std::list<uint8_t> &b){
    std::vector<long long> new_nums;
    int count = 0;
    for (auto it1 = a.rbegin(); it1!=a.rend(); ++it1){
        int _count = count;
        for (auto it2 = b.rbegin(); it2!=b.rend(); ++it2){
            if (count == 0){
                new_nums.push_back(int(*it1) *  int(*it2));
            } else {
                new_nums[_count] += int(*it1) *  int(*it2);
            }
            _count ++;
        }
        new_nums.push_back(0);
        count++;
    }
    while (new_nums.back() == 0 && new_nums.size() > 1)
        new_nums.pop_back();
    for (int i=0; i < new_nums.size() -1; ++i){
        new_nums[i + 1] += new_nums[i] / (base() * base());
        new_nums[i] = new_nums[i] % (base() * base());
    }
    while (new_nums.back() >= base() * base()) {
        new_nums.push_back(new_nums.back() / (base() * base()));
        new_nums[new_nums.size() - 2] = new_nums[new_nums.size() - 2] % (base() * base());
    }
    std::list<uint8_t> _nums = {};
    for (auto it=new_nums.rbegin(); it!=new_nums.rend(); ++it)
        _nums.push_back(*it);
    return _nums;
}

BigInt& BigInt::operator*=(const BigInt& x) {
    std::list<uint8_t> new_nums;
    if (length() >= x.length())
        new_nums = _multiply(x.nums, nums);
    else
        new_nums = _multiply(nums, x.nums);
    nums = new_nums;
    neg = (!x.neg && neg) || (x.neg && !neg);
    return *this;
}


BigInt BigInt::operator*(const long long& x) const {
    BigInt i = *this;
    i *= x;
    return i;
}

BigInt& BigInt::operator*=(const long long& x) {
    BigInt i = x;
    return *this *= i;
}

BigInt BigInt::operator/(const BigInt& x) const {
    BigInt i = *this;
    i /= x;
    return i;
}

BigInt& BigInt::operator/=(const BigInt& x) {
    std::list<uint8_t> new_nums;
    BigInt  dividend = this->abs();
    BigInt divisor = x.abs();
    if (dividend < divisor)
    {
        nums = {0};
    } else {
        nat answer;
        BigInt tmp = *this;
        tmp.nums = {};
        for (auto num : dividend.nums){
            answer.push_back(0);
            tmp.nums.push_back(num);
            while (tmp >= divisor){
                tmp -= divisor;
                answer.back() += 1;
            }

        }
        // 删除高位的0
        while (answer.size() > 1){
            if (answer.front() == 0)
                answer.pop_front();
            else
                break;
        }
        nums = answer;
    }
    neg = (!x.neg && neg) || (x.neg && !neg);
    return *this;
}

BigInt BigInt::operator/(const long long& x) const {
    BigInt i = *this;
    i /= x;
    return i;
}

BigInt& BigInt::operator/=(const long long& x) {
    BigInt i = x;
    return *this /= i;
}


int BigInt::compare(const BigInt& x) const {
    if (neg && !x.neg) return -1;
    if (!neg && x.neg) return 1;
    int check = -1;
    if (!neg && !x.neg) check=1;
    if (nums.size() > x.nums.size()) return check;
    if (nums.size() < x.nums.size()) return -1 * check;
    auto it1 = nums.begin();
    auto it2 = x.nums.begin();
    while(it1!=nums.end()){
        if (*it1 > *it2) return check;
        if (*it1 < *it2) return -1  * check;
        ++it1;
        ++it2;
    }
    return 0;
}

bool BigInt::operator<(const BigInt& x) const{
    return compare(x) == -1;
}

bool BigInt::operator<=(const BigInt& x) const{
    int compared = compare(x);
    return compared == -1 || compared == 0;
}

bool BigInt::operator>(const BigInt& x) const{
    return compare(x) == 1;
}

bool BigInt::operator>=(const BigInt& x) const{
    int compared = compare(x);
    return compared == 1 || compared == 0;
}

bool BigInt::operator==(const BigInt& x) const{
    return compare(x) == 0;
}

bool BigInt::operator!=(const BigInt& x) const{
    return !(*this == x);
}

// 相当于将256进制的数转换为10进制
std::ostream &operator<<(std::ostream &out, BigInt const &x) {
    std::vector<int> res;
    res.push_back(0);
    for (auto num: x.nums) {
        for (auto &j : res)
            j *= x.base() * x.base();

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

    if (x.neg)
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
