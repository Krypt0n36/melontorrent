import socket
import binascii
import struct


peers_bytes = binascii.unhexlify('6f2514363a98d598b0fb0001db81aa0aaebddaa4186d3ae4da12a34c6a32cdb973fdc8d5cab273f41ae1c5e7b0e41ae1c220ebb7ee69bc1d48c49e21b9965e4b5ef4b9816e2bc8d5b5d7b617c4edb5d6a671c4edb0dd79a7f67ca996c651dfb8a58c181e1aeba58c181e1aeaa58c181e1ae9a58c181e1ae8a58c181e1ae7a58c181e1ae6a58c181e1ae5a58c181e1ae4a58c181e1ae3a58c181e1ae2a58c181e1ae18efe522ea1608ac70c38c8d568dae962f8e96793a14b1ae162610d591f906176d2781ae15f46fe7ac8d55e311ff4c00858e68e0d1ae1566b37f041f1563170f041f15439f5e71f4053e41835ff984e2ae89eca35473afc7a1ec9322f5eaf41f11899326ac8d5187a9a43c8d5175ef76efe8105f684e69f6f023874ee97d9')

print(len(peers_bytes))


def f1():
    for i in range(0, len(peers_bytes) // 6):
        # Method 1
        couple = peers_bytes[i*6: i*6+6]
        ip1 = socket.inet_ntoa(couple[0:4])
        port1 = couple[5] + couple[4]*256
        # Method 2
        start = i * 6
        end = start + 6
        ip2 = socket.inet_ntoa(peers_bytes[start:(end - 2)])
        raw_port = peers_bytes[(end - 2):end]
        port2 = raw_port[1] + raw_port[0] * 256

        print('%s:%d <=> %s:%d'%(ip1, port1, ip2, port2))


f1()