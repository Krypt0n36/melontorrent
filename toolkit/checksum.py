import hashlib



def __main__(inp):
    h = hashlib.sha1()
    h.update(inp)
    return h.digest()
