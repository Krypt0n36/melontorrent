import hashlib
import json
from toolkit  import bencoder, checksum
import requests
from toolkit.bootstrap import generatePeerId
import binascii
import urllib.parse
import struct
import sys
import socket

peer_id = 'ABCDEFGHIJKLMNOPQRST'



def viaHTTP(tracker, paramsObject):
    print('[~] Requesting peers list from tracker via HTTP.')
    h = urllib.parse.quote_from_bytes(paramsObject['info_hash']) # Encode the hash from bytes to url compatible byte array.
    params = '?info_hash=' + h + '&peer_id=' + peer_id
    url = tracker + params
    r = requests.get(url)
    if r.status_code != 200:
        print('[!] Tracker responded with `%d` HTTP code.'%r.status_code)
        return False
    return bencoder.parsePeersFromResponse(r.content)

def viaUDP(tracker, paramsObject):
    print('[~] Requesting peers list from tracker via UDP.')
    addr = tracker[tracker.find('udp://')+6:tracker.find(':', 5)]
    port = tracker[tracker.find(':', 5)+1:]
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print(tracker)
    print(addr, port)  
    #packet = struct.pack('qiis', 0x41727101980, 0, 0x422)
    #packet = struct.pack('>qii',8 ,4497486125440, bytearray([0x0]*8), paramsObject['info_hash'], peer_id.encode())
    
    #packet = struct.pack('>qii',0x41727101980 , 0, 0x66)
    packet = binascii.unhexlify('000004172710198000000000be379f57')

    print(binascii.hexlify(packet))
    s.sendto(packet, (addr, int(port)))
    d = s.recv(1024)
    print(d)
    peers = []
    return peers    

def bootstrap(torrent_file):
    tobj = bencoder.decodeFile(torrent_file)[1][0]
    info_obj = tobj['info']
    #print(info_obj)
    annouce_list = tobj['announce-list']
    info_section = bencoder.encode(info_obj)
    hash = checksum.__main__(info_section)
    # Peers list
    peers = []
    for tracker in annouce_list:
        tracker = tracker[0]
        if tracker[0:4] == 'http': # HTTP Tracker
            peers = peers + viaHTTP(tracker, {
                'info_hash':hash,
                'peer_id':peer_id
        })
        else:
            print('[!] UDP tracker communication is not supported yet.')
            '''
            peers = peers + viaUDP(tracker, {
                'info_hash':hash,
                'peer_id':peer_id
            })
            '''         
    print(peers)


bootstrap(sys.argv[1])