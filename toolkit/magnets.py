from urllib.parse import unquote 

# Parse parameters of torrent magnet string.
def parseMagnet(magnet_string):
    duos = magnet_string[8:].split('&')
    out = {}
    for duo in duos:
        name = duo.split('=')[0]
        value = duo.split('=')[1]
        # Decode URL if data name is tr
        if name == 'tr':
            value = unquote(value)
        if name == 'xt':
            value = value.split(':')
        out[name] = value
    return out


print(parseMagnet('magnet:?xt=urn:btih:BCW2LJ5GDA5K4HQJ3AY56Z2I2VTASWQQ&dn=Sintel&tr=udp%3A%2F%2Ftracker.leechers-paradise.org%3A6969'))