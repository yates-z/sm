//
// Created by admin on 2022/6/7.
//

#include "bytes.h"

string Bytes::bytesToHexString(const bytes& byteArr)
{
    if (byteArr.empty()) {
        return "";
    }
    std::string buff;
    for (byte b: byteArr){
        int high = b / 16, low = b % 16;
        buff += (high < 10) ? ('0' + high) : ('a' + high - 10);
        buff += (low < 10) ? ('0' + low) : ('a' + low - 10);
    }
    return buff;
}

bytes Bytes::hexStringToBytes(const string &hex)
{
    auto byteLen = hex.length() / 2;
    string strByte;
    unsigned int n;
    bytes b;
    for (int i = 0; i < byteLen; i++)
    {
        strByte = hex.substr(i * 2, 2);
        sscanf_s(strByte.c_str(), "%x", &n);
        b.push_back(n);
    }
    return b;
}

bytes Bytes::stringToBytes(const string &str)
{
    bytes b;
    byte* ch_ptr = (byte*)str.c_str();

    for (int i=0; ch_ptr && ch_ptr[i]; i++)
        b.push_back(ch_ptr[i]);
    return b;
}


int hex2int(char c)
{
    if ((c >= 'A') && (c <= 'Z'))
    {
        return c - 'A' + 10;
    }
    else if ((c >= 'a') && (c <= 'z'))
    {
        return c - 'a' + 10;
    }
    else if ((c >= '0') && (c <= '9'))
    {
        return c - '0';
    }
}

#include <iostream>
uint64_t Bytes::hexStringToUint64(const string &str) {
    uint64_t x;
    std::stringstream ss;
    ss << std::hex << "FFFFFFFFFFFFFFFFF";
    ss >> x;
    std::cout << x << std::endl;
    return x;
}