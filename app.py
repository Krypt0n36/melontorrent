from qbittorrent import Client



qb = Client('http://localhost:5050')
qb.login('admin', 'password')

torrents = qb.torrents()

for torrent in torrents:
    print(torrent['name'])
