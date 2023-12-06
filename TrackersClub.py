


class TrackersClub:
    def __init__(self):
        self.trackers = []

    def addTracker(self, tracker, nb_peers):
        self.trackers.append((tracker, nb_peers))
        return True
    
    def listTrackers(self):
        for tracker in self.trackers:
            print('%s\t%d Peer(s)'%(tracker[0], tracker[1]))