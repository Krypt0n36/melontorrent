import socket
import time
from threading import Thread
import binascii


'''
    FIFO BASED CONCURRENT PIPE THAT SIMULATES
    APPLICATION LAYER NETWORK BUFFER.
'''
class NetworkPipe(Thread):
    def __init__(self, conn, logger):
        Thread.__init__(self)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(5)
        self.logger = logger
        self.buffer = b''
        self.conn = conn
        self.connected = -1
        self.watch = True # Watch for network buffer
        self.timeout = 4 # Timeout value in seconds
        self.shared = b'' # Instance used to share data accross threads.

    def run(self):
        if self.initConnection():
            self.watchDog()

    def initConnection(self):
        self.logger.info('Connecting to peer.')
        try:
            self.sock.connect(self.conn)
            self.connected = True
            self.logger.success('Connection maintained.')
        except socket.error:
            self.connected = False
            return False
        return True
    
    def sendData(self, data):
        try:
            self.sock.send(data)
        except socket.error:
            # Connection lost
            self.logger.info('Connection with peer lost.')
            self.connected = False


    def clearBuffer(self):
        self.buffer = b''
        return True
    
    def watchDog(self):
        self.logger.info('Watch dog started..')
        while self.watch:
            try:
                buff = self.sock.recv(1024)
            except socket.error as e:
                self.logger.error('Socket error ' + str(e))
                continue
            if len(buff) > 0:
                self.buffer += buff
            time.sleep(1)

    def read(self, size, size_strict=False):
        while (size_strict==True) and (len(self.buffer) < size):
            time.sleep(2)

        self.shared = b''
        if size > len(self.buffer):
            self.shared = self.buffer
            self.buffer = b''
        else:
            self.shared = self.buffer[:size]
            self.buffer = self.buffer[size:]

