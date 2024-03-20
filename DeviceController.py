from typing import List, Optional
from Device import Device




class DeviceController:

    def __init__(self) -> None:
        self.devices: List[Device] = []


    def add(self, device: Device)->None:
        self.devices.append(device)


    def remove(self, reference: Device)->None:
        self.devices = [device for device in self.devices if device.ip != reference.ip]

    def getDevice(self, ip:str)->Optional[Device]:
        for device in self.devices:
            if device.ip == ip:
                return device
        return None
    
    def printDevices(self)->None:
        print("------ DEVICES ------- \n")
        for device in self.devices:
            print(f"IP: {device.ip} -- Nombre: {device.name}  -- System: {device.system}")



