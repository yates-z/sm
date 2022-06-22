project(sm)
set(CMAKE_CXX_STANDARD 11)

add_executable(sm bytes.cpp sm3.cpp sm2.cpp curve.cpp bigInt.cpp)