import logging


class DataMedium:
    def __init__(self):
        self.peers = [] # Online peers
        self.peers_addrs = []
    
    def addPeer(self, peer):
        if not (peer in self.peers):
            self.peers.append(peer)
            return True
        return False
    
    def addPeersAddrs(self, peer_addrs):
        self.peers_addrs += peer_addrs