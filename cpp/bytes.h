//
// Created by admin on 2022/6/7.
//

#ifndef SM_BYTES_H
#define SM_BYTES_H

#include <string>
#include <cstdint>
#include <vector>
#include <sstream>

using std::string;
using std::vector;

typedef uint8_t byte;
typedef vector<byte> bytes;

class Bytes
{
public:
    Bytes() = default;
    static string bytesToHexString(const bytes&);
    static bytes hexStringToBytes(const string&);
    static bytes stringToBytes(const string&);
    static uint64_t hexStringToUint64(const string&);
};

#endif //SM_BYTES_H
