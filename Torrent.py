from toolkit import bencoder
import sys
import logging
import hashlib
import os
from threading import Thread

class Torrent():
    def __init__(self):
        self.announce:str = ''
        self.announce_list: list = []
        self.info_hash:bytes = b''
        self.info: list = []

    '''
        Takes `info` as object from main torrent object, convert it back to bencoded format
        then hash it using sha1.
    '''
    def hashInfo(self, info:object) -> bytes : 
        bc = bencoder.encode(info)
        h = hashlib.sha1()
        h.update(bc)
        return h.digest()

    '''
        Read and parse torrent from file.
    '''
    def fromFile(self, filepath:str):
        # Convert possible relative path to absolute path
        filepath = os.path.join(os.path.dirname(__file__), filepath)
        # Check if file exists
        try:
            f = open(filepath, 'rb')
        except FileNotFoundError:
            logging.error("[!] Torrent file seem not to exist under `{filepath}`.".format(filepath=filepath))
            return False
        content = f.read()
        f.close()
        size, torrent_obj = bencoder.decode(content)
        
        if not torrent_obj:
            logging.error("[!] Error while parsing torrent file.")
            return False

        self.announce_list = torrent_obj[0]['announce-list']
        self.announce_list.append([self.announce])
        self.info = torrent_obj[0]['info']
        self.info_hash = self.hashInfo(self.info)

        

    def fromMagnet(magnet:str):
        pass

    def saveFile(torrent_obj:object, under=None) -> int:
        bs = bencoder.encode(torrent_obj)
        f = open(under, 'wb')
        f.write(bs)
        f.close()
        return len(bs)

