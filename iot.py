class Iot:
    ip_address :str
    connected: bool

    def __init__(self, ip_address) -> None:
        self.ip_address = ip_address
        self.connected = False

    def connect(self):
        raise NotImplementedError("interfaccia Iot non ha il metodo handshake")

    def getDeviceInfo(self):
        raise NotImplementedError("interfaccia Iot non ha il metodo getDeviceInfo")

    def isOn(self):
        raise NotImplementedError("interfaccia Iot non ha il metodo isOn")

    def turnOn(self):
        raise NotImplementedError("interfaccia Iot non ha il metodo turnOn")

    def turnOff(self):
        raise NotImplementedError("interfaccia Iot non ha il metodo turnOff")