import os
import json
import sys


VERBOSE=False
DEV=True
# Bencoding modules
def bencodingParser(inp_filepath: str="", f=None, recCall=False):
    # Open file for binary reading if file is not already opened (Recursive behaviour)
    if not recCall:
        print("[~] File is closed, reopening.")
        f = open(inp_filepath, 'rb')
    # Start by inspecting the first byte
    eqobj = {} # Dictionary equivalent of metadata.
    fid = 0 # Field ID
    size = os.path.getsize(inp_filepath)
    while f.tell()<size:
        # Future revision.
        instruction_type=''
        instruction_code = str(f.read(1).decode('ascii'))
        if instruction_code.isnumeric():
            # Case 1 : String
            isize = instruction_code
            while (c:=str(f.read(1).decode('ascii')))!=':':
                isize = isize + c   
            isize = int(isize)
            # Check if data readable or binary
            try:
                data = str(f.read(isize).decode('ascii'))
            except UnicodeDecodeError:
                data = str(f.read(isize))
            eqobj[fid] = data
            fid += 1
            instruction_type = 'String'
        elif instruction_code == 'i':
            # Case 2 : Number
            e = f.tell()
            data = ''
            while (c:=str(f.read(1).decode('ascii')))!='e':
                data = data + c
            # To revise.
            data = int(data) # Allowing `integer` bencode to contain signed and floating points. 
            eqobj[fid] = data
            fid += 1
            instruction_type = 'Integer'
        elif instruction_code == 'd':
            # Case 3 : Dictionary
            data = bencodingParser(inp_filepath, f, True)
            eqobj[fid] = data
            fid += 1
            instruction_type = 'Dictionary'
        elif instruction_code == 'e':
            # Case 3.5 : End of a dictionary, we are inside a recursive call
            # This cannot happen during an initial call.
            if recCall: # Check if this call is recursive.
                print("[~] Returning from a recursive call, " + str(f.tell()))
                return eqobj
        print('%d/%d'%(f.tell(), size))
        # DEV LOGGING START
        if DEV:
            if instruction_type != '':
                print('[~] Instruction found.')
                print('[~] Type  : `%s`'%instruction_type)
                print('[~] Value : `%s`'%data)
            else:
                print('[~] Unexpected.')

    return eqobj

def prettifyLogically(messy_dic):
    nice_dic = {}
    for i in range(0, len(messy_dic), 2):
        if type(messy_dic[i+1]).__name__ == 'dict':
            # Multi-depth
            nice_dic[messy_dic[i]] = prettifyLogically(messy_dic[i+1])
        else:
            nice_dic[messy_dic[i]] = messy_dic[i+1]
    return nice_dic


if __name__ == '__main__':
    if len(sys.argv)>=2:
        info = bencodingParser(sys.argv[1])
        if '-p' in sys.argv:
            info = prettifyLogically(info)
        print(info)
    else:
        print('USAGE: ')
        print('./md-reader.py [Torrent file path]')





