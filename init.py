from server import Server



if __name__ == "__main__":
    server = Server()
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
    finally:
        server.close()
