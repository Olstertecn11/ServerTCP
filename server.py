import socket
from threading import Thread
from jsonTool import is_valid, getObject
from DeviceController import DeviceController
from Device import Device

class Server:
    def __init__(self, port=65432, ip='0.0.0.0'):
        self.port = port
        self.controller: DeviceController = DeviceController()
        self.ip = ip
        self.connected_clients = []
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.codes_dictionary = {
            "200": self.controller.add,
            "203": self.controller.remove
        }

    def execute_action(self, code, *args, **kwargs):
        if code in self.codes_dictionary:
            funcion = self.codes_dictionary[code]
            return funcion(*args, **kwargs)
        else:
            print("Código no encontrado")

    def analyze_request(self, request, ip):
        if is_valid(request):
            object_request = getObject(request)
            code_request = object_request["code"]
            print(f"code: {code_request}")
            device = Device(ip, object_request["username"], object_request["system"])
            self.execute_action(str(code_request), device)
            # Transmitir el mensaje a todos los demás dispositivos conectados

    def start_client_handling(self, conn, addr):
        print('Conexión establecida por', addr)
        self.connected_clients.append((conn, addr))
        try:
            self.controller.printDevices()
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                print('Mensaje recibido:', data.decode())
                self.broadcast_message(data.decode(), exclude=addr[0])
                self.analyze_request(data, addr)

        except ConnectionResetError:
            print('Dispositivo {} ha salido de la sesión'.format(addr[0]))
            self.connected_clients.remove((conn, addr))
            conn.close()

    def start(self):
        self.server.bind((self.ip, self.port))
        self.server.listen()
        print('Server listening on: ', (self.ip, self.port))

        while True:
            conn, addr = self.server.accept()
            client_thread = Thread(target=self.start_client_handling, args=(conn, addr))
            client_thread.start()

    def broadcast_message(self, message, exclude=None):
        encoded_message = message.encode()  
        for client_conn, client_addr in self.connected_clients:
            if exclude and client_addr[0] == exclude:
                continue
            client_conn.sendall(encoded_message)

    def close(self):
        self.server.close()

