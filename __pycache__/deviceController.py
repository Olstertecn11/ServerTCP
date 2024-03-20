from Device import Device
from typing import List

class DeviceController:


    def __init__(self):
        self.devices:List[Device] = []
    

    def add(self, new_device:Device):
        self.devices.append(new_device)


    def remove(self, _id:str):
        filtered_devices = list(filter(lambda))

