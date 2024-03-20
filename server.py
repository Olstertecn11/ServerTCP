import socket
from jsonTool import is_valid, getObject

class Server:
    def __init__(self, port=65432, ip='0.0.0.0'):
        self.port = port
        self.ip = ip
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    

    def analyze_request(self, request):
        if(is_valid(request)):
            object_request = getObject(request)
            code_request = object_request["code"]
            print(f"Code: {code_request}")
            print(f"Request: {object_request}")




    def start(self):
        self.server.bind((self.ip, self.port))
        self.server.listen()
        print('Server listening on: ', (self.ip, self.port))
        conn, addr = self.server.accept()
        print('Conexión establecida por', addr)
        while True:
            data = conn.recv(1024)
            if not data:
                break
            self.analyze_request(data)
            print('Mensaje recibido:', data.decode())
            conn.sendall(data)
        conn.close()

    def close(self):
        self.server.close()


