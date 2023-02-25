import os
import json

# Bencoding modules

def bencodingParser(inp_filepath: str="", f=False):
    # Open file for binary reading if file is not already opened (Recursive behaviour)
    if f==False or f.closed:
        print("[~] File is closed, reopening.")
        f = open(inp_filepath, 'rb')
    # Start by inspecting the first byte
    eqobj = {} # Dictionary equivalent of metadata.
    fid = 0 # Field ID
    size = os.path.getsize(inp_filepath)
    while f.tell()<size:
        # Future revision.
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
        elif instruction_code == 'i':
            # Case 2 : Number
            e = f.tell()
            value = ''
            while (c:=str(f.read(1).decode('ascii')))!='e':
                value = value + c
            # To revise.
            value = float(value) # Allowing `integer` bencode to contain signed and floating points. 
            eqobj[fid] = value
            fid += 1
        elif instruction_code == 'd':
            # Case 3 : Dictionary
            obj = bencodingParser(inp_filepath, f)
            eqobj[fid] = obj
            fid += 1
        elif instruction_code == 'e':
            # Case 3.5 : End of a dictionary, we are inside a recursive call
            # This cannot happen during an initial call.
            return eqobj
        else:
            # Caracter expected. Discard!
            pass
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
