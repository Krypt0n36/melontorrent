import time
import json
import os
import binascii

'''
    WRITE LOGS AND VARIABLES TO DISK FOR DEBUGGING
'''
class SuperLogger():
    def __init__(self, session, workspace):
        self.session = session
        self.workspace = workspace
        os.makedirs('Logs/'+self.session, exist_ok=True)
        self.logf_path = 'Logs/'+self.session+'/'+self.workspace+'.html'
        self.max_depth = 4 # Max depth for state objects
        self.f = open(self.logf_path, 'a')
           
    def store(self, message):
        self.f.write(message)
        self.f.flush()

    def success(self, message, mute=True):
        message = str(message)
        if not mute:
            print(u'\u001b[32m[+]\u001b[0m ' + message)
        self.store('[+] ' + message + '\n')


    def error(self, message, mute=True):
        message = str(message)
        if not mute:
            print(u'\u001b[31m[!]\u001b[0m ' + message)
        self.store('[!] ' + message + '\n')

    def info(self, message, muted=True):
        message = str(message)
        if not muted:
            print(u'\u001b[34m[~]\u001b[0m ' + message)
        self.store('[~] ' + message + '\n')

    def terminate(self):
        self.f.close()
