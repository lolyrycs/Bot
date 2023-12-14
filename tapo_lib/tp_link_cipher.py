from Crypto.Cipher import AES, PKCS1_v1_5
from Crypto.PublicKey import RSA
from pkcs7 import PKCS7Encoder
from base64 import b64decode, b64encode

class TpLinkCipher:
    iv :bytearray
    key :bytearray

    def __init__(self, key, iv):
        self.key = key
        self.iv = iv

    def encrypt(self, data:str):
        data = PKCS7Encoder().encode(data)
        cipher = AES.new(bytes(self.key), AES.MODE_CBC, bytes(self.iv))
        encrypted = cipher.encrypt(data.encode("UTF-8"))
        return b64encode(encrypted).decode("UTF-8").replace("\r\n","")

    def decrypt(self, data: str):
        aes = AES.new(bytes(self.key), AES.MODE_CBC, bytes(self.iv))
        pad_text = aes.decrypt(b64decode(data.encode("UTF-8"))).decode("UTF-8")
        return PKCS7Encoder().decode(pad_text)
