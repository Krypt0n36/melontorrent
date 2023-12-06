import socket
from threading import Thread
import hashlib
import binascii
from NetworkPipe import NetworkPipe
import time
import logging
from SuperLogger import SuperLogger
import struct

class Peer(Thread):
    def __init__(self, data_medium, peer, info_hash, session):
        Thread.__init__(self)
        self.data_medium = data_medium
        self.host = peer[0]
        self.port = peer[1]
        self.group = info_hash
        self.online = False
        # Peer states
        self.chocked = True
        self.interested = False
        # Initialize superlogger
        self.logger = SuperLogger(session,f'{self.host}-{self.port}')
        # Fire NetworkPipe
        self.logger.info('Peer Initializing network pipe.')
        self.networkPipe = NetworkPipe((self.host, self.port), self.logger)
        self.networkPipe.start()



    def run(self):
        # Wait for network pipe to init connection
        self.logger.info('Waiting for network pipe to connect.')
        seconds = 0
        while self.networkPipe.connected == -1:
            if seconds > 10:
                self.logger.error('Peer Connecting to peer taking too long.')
                break
            time.sleep(1)
            seconds += 1

        if self.networkPipe.connected == True:
            self.logger.info('Connection to remote peer successful. Performing handshake..')
            if not self.handshake():
                self.logger.info('Handshake failed. Aborting..')
        else:
            self.logger.error('Cannot connect to peer. Aborting..')

        self.terminate()

    def terminate(self):
        self.logger.error('Terminating peer..')
        self.networkPipe.watch = False
        self.networkPipe.join()

    def parse_response(self):
        # Decode the response as a BitTorrent message
        self.networkPipe.read(5, True)
        data = self.networkPipe.shared

        # Extract the message length
        length = struct.unpack("!I", data[:4])[0]
        # Extract the message ID
        msg_id = data[4]
        # Handle the message based on its ID
        if msg_id == 0: # Choke message
            return ("choke",)
        elif msg_id == 1: # Unchoke message
            return ("unchoke",)
        elif msg_id == 2: # Interested message
            return ("interested",)
        elif msg_id == 3: # Not interested message
            return ("not interested",)
        elif msg_id == 4: # Have message
            self.networkPipe.read(4, True)
            piece_index = struct.unpack("!I", self.networkPipe.shared)[0]
            return ("have", piece_index)
        elif msg_id == 5: # Bitfield message
            self.networkPipe.read(length - 5, True)
            return ("bitfield", self.networkPipe.shared)
        elif msg_id == 6: # Request message
            piece_index, block_offset, block_length = struct.unpack("!III", data[5:])
            return ("request", piece_index, block_offset, block_length)
        elif msg_id == 7: # Piece message
            piece_index, block_offset = struct.unpack("!II", data[5:13])
            block_data = data[13:]
            return ("piece", piece_index, block_offset, block_data)
        elif msg_id == 8: # Cancel message
            piece_index, block_offset, block_length = struct.unpack("!III", data[5:])
            return ("cancel", piece_index, block_offset, block_length)
        else:
            return ("unkown-command", str(msg_id))


    # Constantly interact with peer and parse each recieved data.
    # Needs to run right after handshake
    def interact(self):
        while True:
            if len(self.networkPipe.buffer) > 0:
                parsed = self.parse_response()
                self.logger.info('Parsing function result : ' + str(parsed))
            else:
                time.sleep(2)

    def handshake(self):
        if self.networkPipe.connected != True:
            self.logger.error('Connection to peer is lost, therefore cannot perform handshake.')
            return False
        self.logger.info('Sending handshake..')
        handshake = b''
        handshake += chr(19).encode()
        handshake += b'BitTorrent protocol'
        handshake += (chr(0)*8).encode()
        handshake += self.group
        handshake += hashlib.sha1(b'zebi').digest()

        self.networkPipe.sendData(handshake)
        

        self.interact()
        self.networkPipe.read(68, True)

        response = self.networkPipe.shared


        self.logger.info('Handshake response received, checking..')
        # PARSE HANDSHAKE RESPONSE
        if len(response) != 68:
            self.logger.error('Handshake response check test failed, aborting.. ' + str(len(response)))
            self.logger.info(binascii.hexlify(response))
            return False

        info_hash = response[28: 48]

        if info_hash != self.group:
            self.logger.error(
                'Peer responded with different info hash during handshake.')
            self.logger.info('Proper info hash : ' %
                          binascii.hexlify(self.group))
            self.logger.info('Responded info hash : ' %
                          binascii.hexlify(info_hash))
            return False

        self.logger.success('Handshake finished successfully.')


        return True
