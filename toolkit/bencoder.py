
import os
import binascii
import hashlib
from struct import unpack


def filestreamDecoder_(inp_filepath: str = "", f=None, recDepth=0, expectedOutputType='dict'):
    # Open file for binary reading if file is not already opened (Recursive behaviour)
    # Start by inspecting the first byte
    if expectedOutputType == 'dict':
        res = {}  # Dictionary equivalent of metadata.
    else:
        res = []
    size = os.path.getsize(inp_filepath)

    data_name = ''  # Holds current extracted data's name
    while f.tell() < size:
        # Future revision.
        instruction_code = str(f.read(1).decode('ascii'))
        if instruction_code.isnumeric():
            # Case 1 : String
            isize = instruction_code
            while (c := str(f.read(1).decode('ascii'))) != ':':
                isize = isize + c
            isize = int(isize)
            # Save file cursor position
            p = f.tell()
            # Check if data readable or binary
            hex = False
            try:
                data = f.read(isize).decode('ascii')
            except UnicodeDecodeError:
                f.seek(p)
                data = binascii.hexlify(f.read(isize))
                hex = True

            if type(res).__name__ == 'dict':
                if data_name == '':
                    data_name = data
                    print(data_name)
                else:

                    if hex:
                        res[data_name] = '<hex>' + data.decode() + '</hex>'
                    else:
                        res[data_name] = data
                    data_name = ''
            else:
                res.append(data)
        elif instruction_code == 'i':
            # Case 2 : Number
            data = ''
            while (c := str(f.read(1).decode('ascii'))) != 'e':
                data = data + c
            # To revise.
            # Allowing `integer` bencode to contain signed and floating points.
            data = int(data)
            if type(res).__name__ == 'dict':
                if data_name == '':
                    data_name = data
                else:
                    res[data_name] = data
                    data_name = ''
            else:
                res.append(data)
        elif instruction_code == 'd':
            # Case 3 : Dictionary
            data = filestreamDecoder_(inp_filepath, f, recDepth+1, 'dict')
            if type(res).__name__ == 'dict':
                if data_name == '':
                    pass
                else:
                    res[data_name] = data
                    data_name = ''
            else:
                res.append(data)
        elif instruction_code == 'l':
            # Case 4 : List
            data = filestreamDecoder_(inp_filepath, f, recDepth+1, 'array')
            # Convert data from object to list
            if type(res).__name__ == 'dict':
                if data_name == '':
                    pass
                else:
                    res[data_name] = data
                    data_name = ''
            else:
                res.append(data)
            instruction_type = 'List'
        elif instruction_code == 'e':
            # Case 3.5 : End of a dictionary, we are inside a recursive call
            # This cannot happen during an initial call.
            if recDepth > 0:  # Check if this call is recursive.
                return res

    return res


def filestreamDecoder(filepath):
    f = open(filepath, 'rb')
    res = filestreamDecoder_(filepath, f, 0, 'array')[0]
    f.close()
    return res


# Append result to `res` according to its result.
def append_to_result(res, value, name=''):
    if type(res).__name__ == 'dict':
        if name != '':
            res[name] = value
    else:
        res.append(value)
    return res


def decode(input_data, cursor=0, ret_type='list', depth=0):
    # Choose current data block container type, helps for recursive calls.
    # Field name, get cleared every even iteration.
    field_name = ''
    if ret_type == 'dict':
        res = {} 
    else:
        res = []
    while cursor < len(input_data):
        c = chr(input_data[cursor])
        #input()
        if c.isnumeric(): # Case I : String
            col = input_data.find(b':', cursor)
            data_length = int(input_data[cursor:col])
            # Handle data depending on its type
            try:
                data_content = input_data[col+1: col+data_length+1].decode()
                # Manually check if its a peers list to force convert it to string
                if field_name == 'peers':
                    raise Exception('Peers force to hex.')
            except Exception:
                data_content = binascii.hexlify(input_data[col+1: col+data_length+1])
                data_content = '<HEX>' + data_content.decode() + '</HEX>'
            if type(res).__name__ == 'dict':
                if field_name != '':
                    res[field_name] = data_content
                    field_name = ''
                else:
                    field_name = data_content
            else:
                res.append(data_content)
            cursor = col + data_length + 1
        elif c == 'i': # Case II : Integer
            e = input_data.find(b'e', cursor)
            data_content = input_data[cursor+1:e].decode()
            if type(res).__name__ == 'dict':
                if field_name != '':
                    res[field_name] = int(data_content)
                    field_name = ''
                else:  
                    field_name = int(data_content)
            else:
                res.append(data_content)
            cursor = e + 1
        elif c == 'l': # Case III: List
            # Recursive call
            cursor, data_content = decode(input_data, cursor+1, 'list', depth+1)
            if type(res).__name__ == 'dict':
                if field_name != '':
                    res[field_name] = data_content
                    field_name = ''
            else:
                res.append(data_content)
        elif c == 'd': # Case IV: Dictionary
            cursor, data_content = decode(input_data, cursor+1, 'dict', depth+1)
            if type(res).__name__ == 'dict':
                if field_name != '':
                    res[field_name] = data_content
                    field_name = ''
            else:
                res.append(data_content)
        elif c == 'e': # End of list or dictionary.,
            cursor+=1
            if depth>0:
                return cursor, res # Return from recursive call
        else:
            print(cursor, 'Garbage')
            cursor+=1

    return cursor, res    

def decodeFile(filepath):
    print(os.path.getsize(filepath))
    f = open(filepath, 'rb')
    content = f.read()
    f.close()
    return decode(content)   

def encode(input_data):
    dec:bytes
    match type(input_data).__name__:
        case 'int':
            dec = b'i' + str(input_data).encode() + b'e'
        case 'str':
            # Check representation
            if input_data.find('<HEX>') == 0:
                hex_string = input_data[input_data.find('<HEX>')+5:input_data.find('</HEX>')]  
                dec = str(int((len(input_data) - 11)/2)).encode() + b':' + binascii.unhexlify(hex_string)
            else:
                dec = str(len(input_data)).encode() + b':' + bytearray(input_data, 'utf-8')
        case 'list':
            dec = b'l'
            for declaration in input_data:
                dec += encode(declaration)
            dec += b'e'
        case 'dict':
            dec = b'd'
            for key in input_data:
                dec += encode(key)
                dec += encode(input_data[key])
            dec += b'e'
        case _:
            print('Unknown')
    return dec


def parsePeersFromResponse(response):
    p = response.find('peers')
    col = response.find(':', p)
    size = int(response[p+5:col])
    peers_compact = response[col+1:col+size+1]

    peers_list = []
    for i in range(0, len(peers_compact)//6):    
        ip = ''
        ip += str(unpack('>B', peers_compact[i:i+1])[0]) + '.'
        ip += str(unpack('>B', peers_compact[i+1:i+2])[0]) + '.'
        ip += str(unpack('>B', peers_compact[i+2:i+3])[0]) + '.'
        ip += str(unpack('>B', peers_compact[i+3:i+4])[0])
        port=unpack('>H', peers_compact[i+4:i+6])
        peers_list.append((ip, port[0]))
    return peers_list
