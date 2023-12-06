from urllib.parse import urlparse
import struct
import random
import socket
from threading import Thread
import logging
import binascii
import hashlib
import urllib
import requests
from toolkit import bencoder

from Peer import Peer

class Tracker(Thread):
    def __init__(self, data_medium, uri:str, info_hash):
        Thread.__init__(self)
        self.uri = uri
        uri_parsed = urlparse(self.uri) 
        self.dataMedium = data_medium
        self.protocol = uri_parsed.scheme.upper()        
        if self.protocol == 'UDP':
            # INITIALISE SOCKET
            self.host = socket.gethostbyname(uri_parsed.netloc.split(':')[0])
            self.port = int(uri_parsed.netloc.split(':')[1])
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.settimeout(5)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Tracker communication config
        self.connection_id = None
        self.transaction_id = None
        self.info_hash = info_hash


    def recv_buff(self):
        data = b''
        source = None
        while True:
            try:
                buff, source = self.sock.recvfrom(4096)
                if len(buff) <= 0:
                    break
                data += buff
            except TimeoutError:
                break
        return data, source
    
    def run(self):
        # Check which protocol to use
        peers = []
        if self.protocol == 'UDP':
            peers = self.reqAnnounceUDP(self.info_hash)
        elif self.protocol in ['HTTP', 'HTTPS']:
            peers = self.reqAnnounceHTTP(self.uri, self.info_hash)
        if peers!=False:
            self.dataMedium.addPeersAddrs(peers)

    def parsePeers(self, peers_bytes):
        peers = []

        for i in range(0, len(peers_bytes) // 6):
            couple = peers_bytes[i*6: i*6+6]
            ip = socket.inet_ntoa(couple[0:4])
            port = couple[5] + couple[4]*256
            peers.append((ip, port))

        return peers
            

    def parseAnnounceResponse(self, resp:bytes):
        logging.info('[~] Parsing Announce response.')
        action = struct.unpack('>I', resp[:4])[0]
        transaction_id = struct.unpack('>I', resp[4:8])[0]
        intervals = struct.unpack('>I', resp[8:12])[0]
        leechers = struct.unpack('>I', resp[12:16])[0]
        seeders = struct.unpack('>I', resp[16:20])[0]
        _peers = resp[20:]
        peers = self.parsePeers(_peers)

        return peers

    def announceRequest(self, info_hash):
        logging.debug('[~] Announce request executed.')
        # Craft announce packet
        packet = b''
        packet += struct.pack('>Q', self.connection_id)
        packet += struct.pack('>I', 1)
        packet += struct.pack('>I', self.transaction_id)
        packet += info_hash
        packet += hashlib.sha1(b'zebi').digest()
        packet += struct.pack('>Q', 0)
        packet += struct.pack('>Q', 0)
        packet += struct.pack('>Q', 0)
        packet += struct.pack('>I', 0)
        packet += struct.pack('>I', 0)
        packet += struct.pack('>I', 0)
        packet += struct.pack('>i', -1)
        packet += struct.pack('>h', 8000)
        
        self.sock.sendto(packet, (self.host, self.port))
        resp, source = self.recv_buff()

        if not resp:
            return False
        
        try:
            return self.parseAnnounceResponse(resp)
        except Exception as e:
            logging.debug('[!] Tracker announce response seem missing some bytes, (see error bellow). discarding..')
            logging.debug(str(e))
            return False

    def reqAnnounceUDP(self, info_hash):
        # UDP HANDSHAKE
        trans_id = random.randint(0, 1000)
        '''
        Handshake packet structure [128bit fixed]
        <connection-id><action><transaction-id>
        - connection-id  : 64 bit.
        - action         : 32 bit.
        - transaction-id : 32 bit. 
        '''
        packet = b''
        packet += struct.pack('>Q', 0x41727101980)
        packet += struct.pack('>I', 0)
        packet += struct.pack('>I', trans_id)

        self.sock.sendto(packet, (self.host, self.port))
        resp, source = self.recv_buff()

        if not resp:
            return False

        # RESPONSE PARSING
        
        if len(resp) >= 16:
            claimed_action = struct.unpack('>I', resp[:4])[0]
            claimed_transaction_id = struct.unpack('>I', resp[4:8])[0]
            self.connection_id = struct.unpack('>Q', resp[8:16])[0]
            if claimed_transaction_id == trans_id:
                self.transaction_id = claimed_transaction_id
                return self.announceRequest(info_hash)
            
        elif len(resp) != 0:
            # Response buffer is missing some bytes
            logging.debug('[!] Tracker announce response is missing some bytes, discarding..')
    
        return False
    
    def reqAnnounceHTTP(self, url, info_hash):
        hash = urllib.parse.quote_from_bytes(info_hash)
        peer_id = urllib.parse.quote_from_bytes(hashlib.sha1(b'zebi').digest())
        params = '?info_hash=' + hash + '&peer_id' + peer_id
        url = urllib.parse.urljoin(url, params)
        r = requests.get(url)

        if r.status_code != 200:
            return False 
        
        try:
            _, announce = bencoder.decode(r.content)
            _peers = bencoder.deformatH2B(announce[0]['peers'])
            peers = self.parsePeers(_peers)
        except Exception as e:
            logging.debug('[!] Error occured while parsing http response, ' + str(e))
            return False
        
        return peers