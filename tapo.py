from datetime import datetime
from requests import Session
from iot import Iot
from tapo_lib.tp_link_cipher import TpLinkCipher
from base64 import b64decode, b64encode
from Crypto.PublicKey import RSA 
from Crypto.Cipher import  PKCS1_v1_5
from hashlib import sha1
from ast import literal_eval

import uuid
import json
import configparser

ERROR_CODES = {
	"0": "Success",
	"-1010": "Invalid Public Key Length",
	"-1012": "Invalid terminalUUID",
	"-1501": "Invalid Request or Credentials",
	"1002": "Incorrect Request",
	"-1003": "JSON formatting error "
}

class Tapo(Iot):
    public_key :str
    _private_key :str
    terminalUUID :str
    email :str
    encodedEmail :str
    password :str
    encodedPassword :str

    session = None
    cookie = None
    cookie_name = "TP_SESSIONID"
    errorCodes = ERROR_CODES

    def __init__(self, ip_address, email=None, password=None) -> None:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                
        super().__init__(ip_address=ip_address)

        if email is None and password is None:
            config = configparser.ConfigParser()
            config.read('tapo_lib/tapo.ini')
            self.email = config["Credentials"]["email"]
            self.password = config["Credentials"]["password"]
        else:
            self.email = email
            self.password = password

        self.terminalUUID = str(uuid.uuid4())
        self.encryptCredentials()
        self.createKeyPair()
        self.connect()

    #region utils
    def createKeyPair(self):
        keys = RSA.generate(1024)
        self._private_key = keys.exportKey("PEM")
        self.public_key  = keys.publickey().exportKey("PEM")
          
    def encryptCredentials(self):
		#Password Encoding
        self.encodedPassword = b64encode(self.password.encode("UTF-8")).decode("UTF-8")
		#Email Encoding
        self.encodedEmail = self.sha_digest_username(self.email)
        self.encodedEmail = b64encode(self.encodedEmail.encode("utf-8")).decode("UTF-8")

    def sha_digest_username(self, data):
        b_arr = data.encode("UTF-8")
        digest = sha1(b_arr).digest()
        sb = ""
        for i in range(0, len(digest)):
            b = digest[i]
            hex_string = hex(b & 255).replace("0x", "")
            if len(hex_string) == 1:
                sb += "0"
            sb += hex_string
        return sb
    
    def login(self):
        self.connected = False
        self.token = None
        URL = f"http://{self.ip_address}/app"
        Payload = {
            "method":"login_device",
            "params":{
                "password": self.encodedPassword,
                "username": self.encodedEmail
            },
            "requestTimeMils": 0,
        }
        headers = {
            "Cookie": self.cookie
        }
        response = self.sendEncryptPayload(Payload=Payload, URL=URL, headers=headers, use_token=False)
        try:
            self.token = json.loads(response).get("result",{}).get("token", None)
            self.connected = True
            print(f"Tapo {self.ip_address} connected")
            return True
        except:
            errorCode = json.loads(response).get("error_code", 0)
            errorMessage = self.errorCodes.get(str(errorCode), "Generic error")
            raise Exception(f"Error Code: {errorCode}, {errorMessage}")
        return False
    
    def sendEncryptPayload(self, Payload, URL=None, headers=None, use_token=True, check_error=True):
        if headers is None:
            headers = { "Cookie": self.cookie }
        if URL is None:
            URL = f"http://{self.ip_address}/app"
            if use_token:
                if self.token is None and use_token:
                    self.connect()
                if self.token:
                    URL += f"?token={self.token}"

        EncryptedPayload = self.tpLinkCipher.encrypt(json.dumps(Payload))

        SecurePassthroughPayload = {
			"method": "securePassthrough",
			"params": {
				"request": EncryptedPayload
			}
		}

        r = self.session.post(URL, json=SecurePassthroughPayload, headers=headers, timeout=2)

        decryptedResponse = self.tpLinkCipher.decrypt(r.json()["result"]["response"])

        if check_error:
            errorCode = json.loads(decryptedResponse).get("error_code", 0)
            if errorCode!= 0:
                errorMessage = self.errorCodes[str(errorCode)]
                raise Exception(f"Error Code: {errorCode}, {errorMessage}")
        
        return decryptedResponse
    
    def exeCommand(self, method, params=None, check_error=True):
        Payload = {
			"method": method,
			"requestTimeMils": 0,
            "terminalUUID" : self.terminalUUID,
		}

        if params:
            Payload["params"] = params
        response = self.sendEncryptPayload(Payload=Payload, check_error=check_error)
        return response
    
    def decode_handshake_key(self, key):
        decode: bytes = b64decode(key.encode("UTF-8"))
        decode2: bytes = self._private_key

        cipher = PKCS1_v1_5.new(RSA.importKey(decode2))
        do_final = cipher.decrypt(decode, None)
        if do_final is None:
            raise ValueError("Decryption failed!")
        b_arr:bytearray = bytearray()
        b_arr2:bytearray = bytearray()
        
        for i in range(0, 16):
            b_arr.insert(i, do_final[i])
            b_arr2.insert(i, do_final[i + 16])

        return (b_arr, b_arr2)
    
    def handshake(self):
        URL = f"http://{self.ip_address}/app"
        Payload = {
			"method":"handshake",
			"params":{
				"key": self.public_key.decode("utf-8"),
				"requestTimeMils": 0
			}
		}
        if self.session:
            self.session.close()
        self.session = Session()
        r = self.session.post(URL, json=Payload, timeout=2)
        handshake_key = r.json()["result"]["key"]

        key, iv = self.decode_handshake_key(handshake_key)
        self.tpLinkCipher = TpLinkCipher(key=key, iv=iv)

        try:
            self.cookie = f"{self.cookie_name}={r.cookies[self.cookie_name]}"
        except:
            errorCode = r.json()["error_code"]
            errorMessage = self.errorCodes[str(errorCode)]
            raise Exception(f"Error Code: {errorCode}, {errorMessage}")
    #endregion

    def connect(self):
        if not self.session or not self.tpLinkCipher or not self.cookie:
            self.handshake()
        if not self.connected or not self.token:
            self.connected = self.login()
        return self.connected

    def turnOn(self):
        method = "set_device_info"
        params = { "device_on": True }
        self.exeCommand(method=method, params=params)

    def turnOff(self):
        method = "set_device_info"
        params = { "device_on": False }
        self.exeCommand(method=method, params=params)

    def isOn(self):
        return self.getDeviceInfo().get("device_on",None)

    #region advanced
    def getDeviceInfo(self):
        method = "get_device_info"
        result = self.exeCommand(method=method, check_error=False)
        return json.loads(result).get("result",{})
    
    def toggleState(self):
        state = self.isOn()
        if state:
            self.turnOff()
        else:
            self.turnOn()

    def getDeviceName(self):
        enc_nick = self.getDeviceInfo().get("nickname","")
        name = b64decode(enc_nick).decode("utf-8")
        return name
    
    def turnDelay(self, delay=1, on=True):
        """
            delay in secondi
            on : True acceso, False spento
        """
        method = "add_countdown_rule"
        params = {
            "delay": int(delay),
			"desired_states": {
                "on": on
            },
			"enable": True,
			"remain": int(delay)
        }
        self.exeCommand(method=method, params=params)
    
    def turnAt(self, date, on=True):
        now = datetime.now()
        delay = date - now
        self.turnDelay(delay=delay.seconds, on=on)
    #endregion

if __name__ =="__main__":
    config = configparser.ConfigParser()
    config.read('tapo_lib/tapo.ini')
    ip = config["Credentials"]["ip"]
    print(ip)
    tp = Tapo(ip)
    tp.turnOn()
    print(tp.isOn())

    name = tp.getDeviceName()
    print(name)

    tp.turnDelay(delay=10, on=False)
    #tp.turnAt(datetime(2023, 12, 13, 17, 25, 0),on=False)