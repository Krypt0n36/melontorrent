import string
import random


def generatePeerId():
    return ''.join(random.choice(string.ascii_lowercase+string.digits) for i in range(0,20))
