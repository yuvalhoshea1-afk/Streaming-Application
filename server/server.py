import socket
from ThreadedClient import ClientThread
from ServerConfig import IP, PORT, MAX_LISTENERS, logger, SERVER_TIMEOUT


class Server:

    def __init__(self, ip: str, port: int, max_listeners: int):
        self._max_listeners = max_listeners
        self._addr = (ip, port)
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        socket.setdefaulttimeout(SERVER_TIMEOUT)

    def run(self):
        # start listening
        self._socket.bind(self._addr)
        self._socket.listen(self._max_listeners)
        logger.info(f"LISTENING AT {self._addr}")
        # getting the clients
        while True:
            conn, addr = self._socket.accept()
            logger.info(f"Got new client {addr}.")
            ClientThread(conn, addr).start()


if __name__ == "__main__":
    my_server = Server(IP, PORT, MAX_LISTENERS)
    my_server.run()
