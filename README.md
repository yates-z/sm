# GM SM/2/3/4 based on python/c++

## Introduce

本库基于https://github.com/ZZMarquis/gm 库改造(go语言)，加解密操作更简单，且实现与该库互相加解密

##### SM2

基于椭圆曲线(ECC)算法实现的非对称加密算法，对标RSA算法，相较于RSA加密算法更快更安全，且加密后的密文长度更短，常用于加密/解密，签名/验签(未实现)

##### SM3

消息摘要算法，可类比MD5，其安全性要高于MD5与SHA-1算法

##### SM4

对称加密算法，对标AES、3DES

