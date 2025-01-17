import socket
import json
import platform
from DeviceController import DeviceController
import getpass
from Device import Device
from jsonTool import is_valid, getObject
from threading import Thread
import time

class Server:
    def __init__(self, port=65432, ip='0.0.0.0'):
        self.port = port
        self.controller = DeviceController()
        self.ip = ip
        self.connected_clients = []
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.collision_sent = {}
        self.codes_dictionary = {
            "200": self.controller.add,
            "203": self.controller.remove
        }
        self.last_message_times = {}

    def execute_action(self, code, *args, **kwargs):
        if code in self.codes_dictionary:
            funcion = self.codes_dictionary[code]
            return funcion(*args, **kwargs)
        else:
            print("Código no encontrado")

    def analyze_request(self, request, ip):
        if is_valid(request):
            object_request = getObject(request)
            if "code" in object_request:
                code_request = object_request["code"]
                print(f"code: {code_request}")
                device = Device(ip, object_request["username"], object_request["system"])
                self.execute_action(str(code_request), device)
            else:
                self.broadcast_message(request, exclude=ip)


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
                if "time" in data.decode():
                    message_json = json.loads(data.decode())
                    message_time = message_json["time"]
                    self.last_message_times[addr[0]] = message_time
                # Verificar colisiones
                if addr[0] not in self.collision_sent or not self.collision_sent[addr[0]]:
                    if self.detect_collision(data, addr[0]):
                        self.send_collision_message(addr[0])
                        self.collision_sent[addr[0]] = True  # Configurar la bandera para este cliente
                else:
                    self.analyze_request(data, addr)

        except ConnectionResetError:
            print('Dispositivo {} ha salido de la sesión'.format(addr[0]))
            self.connected_clients.remove((conn, addr))
            conn.close()


    def detect_collision(self, message, client_ip):
        message_json = json.loads(message.decode())
        message_time = message_json["time"]

        if not self.last_message_times:  # Verificar si el diccionario está vacío
            self.last_message_times[client_ip] = message_time
            return False

        last_message_time = self.last_message_times.get(client_ip, "")
        if last_message_time:
            print(f"Last message time for {client_ip}: {last_message_time}")
            print(f"Current message time for {client_ip}: {message_time}")

            # Comparar los tiempos completos de los mensajes
            if message_time == last_message_time:
                # Si hay colisión, no actualizar el tiempo del último mensaje
                self.send_collision_message(client_ip)
                return True

        # Si no hay colisión, actualizar el tiempo del último mensaje
        self.last_message_times[client_ip] = message_time
        return False

    def start(self):
        self.server.bind((self.ip, self.port))
        self.server.listen()
        print('Server listening on: ', (self.ip, self.port))

        while True:
            conn, addr = self.server.accept()
            client_thread = Thread(target=self.start_client_handling, args=(conn, addr))
            client_thread.start()

    def broadcast_message(self, message, exclude=None):
        for client_conn, client_addr in self.connected_clients:
            if exclude and client_addr[0] == exclude:
                continue
            client_conn.sendall(message)

    def send_collision_message(self, client_ip):
        collision_message = {"code": "collision"}
        encoded_message = json.dumps(collision_message).encode()
        for client_conn, client_addr in self.connected_clients:
            if client_addr[0] == client_ip:
                client_conn.sendall(encoded_message)

    def close(self):
        self.server.close()

