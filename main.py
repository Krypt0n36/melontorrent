from Torrent import Torrent
from Tracker import Tracker
from Peer import Peer
from DataMedium import DataMedium
from TrackersClub import TrackersClub
from NetworkPipe import NetworkPipe


import socket
import logging
from threading import Thread, Lock
from queue import Queue
import sys
import time
import concurrent.futures
import hashlib

class MelonTorrent:
    def __init__(self, filepath):
        self.torrent = Torrent()
        self.torrent.fromFile(filepath)
        self.seeders = 0
        self.leechers = 0
        self.peers = []
        self.session = str(time.time())

    def run(self):
        logging.info('[~] %d trackers found.'%len(self.torrent.announce_list))
        logging.info('[~] Asking trackers for announce.')

        data_medium = DataMedium()
        
        tracker_threads = []
        for t in self.torrent.announce_list:
            t = t[0]
            logging.info('[~]\t- %s \t'%t)
            tracker = Tracker(data_medium, t, self.torrent.info_hash)
            #tracker.run()
            tracker_threads.append(tracker)
            tracker.start()

        logging.info('[~] Waiting for trackers to finish.')
        
        for tt in tracker_threads:
            tt.join()        

        logging.info('[~] %d peers found, connecting..'%len(data_medium.peers_addrs))

        threads = []    
        for peer in data_medium.peers_addrs:
            pt = Peer(data_medium, peer, self.torrent.info_hash, self.session)    
            threads.append(pt)
            pt.start()


        logging.info('[~] Waiting for threads to finish..')

        c = 0
        for thread in threads:
            thread.join()
            c += 1

        logging.info('[~] Dead-end of the program, exiting..')
        
           
        

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app = MelonTorrent('/home/hassan/Downloads/sintel.torrent')
    app.run()
