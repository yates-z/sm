
## Install

方式一:下载源码包安装 

https://github.com/yates-z/sm/releases

```
pip install smpy-x.x.x.tar.gz
```


## Usage

##### SM2

密钥生成

```python
from smpy import SM2

priv_key, pub_key = SM2.generate_key()
priv_key = priv_key.hex()
pub_key = pub_key.hex()
print(priv_key)
print(pub_key)
```

加密

```python
from smpy import SM2

# priv_key, pub_key为str类型
sm2 = SM2(private_key=priv_key, public_key=pub_key)
plain_data = "hello world!"
enc, err = sm2.encrypt(plain_data)
if err:
    raise Exception(err)
print("cipher text:", enc.hex())
```

解密

```python
from smpy import SM2

sm2 = SM2(private_key=priv_key, public_key=pub_key)
decrypted_text, err = sm2.decrypt(enc)
if err:
    raise Exception(err)
print("decrypted-text:", decrypted_text.decode())
```



##### SM3

hash摘要

```python
from smpy import SM3

data = b"test"
sm3 = SM3()
sm3.write(data)
sum = sm3.sum()
print("digest value is: ", sum.hex())
```



##### SM4

加解密（ECB模式）

```python
from smpy import SM4

# key可以是长度不超过16的任意值
key = b"test"
data = "hello world!"
sm4 = SM4(key)
cipherText, err = sm4.encrypt(data)
print(cipherText)
text, err = sm4.decrypt(cipherText)
print(text)
```



加解密（CBC模式）

```python
from smpy import SM4

# key可以是长度不超过16的任意值
key = b"test"
data = "hello world!"
# CBC模式需要初始向量IV，iv参数默认为b'0000000000000000'
sm4 = SM4(key, mode=SM4.Mode.CBC, iv=b"3221")
cipherText, err = sm4.encrypt(data)
print(cipherText)
text, err = sm4.decrypt(cipherText)
print(text)
```

