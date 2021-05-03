import os
from binascii import hexlify

def dir_logfiles():
    return [s for s in os.listdir() if "log" in s]

def nfile(path_name):
    path = path_name.split('/')[0]
    name = path_name.split('.')[-2]
    ext = path_name.split('.')[-1]
    return {'path':path, 'name':name, 'ext':ext}

def datfile_to_dict(file_path, scalar=1.0):
    count = 0
    data = []
    with open(file_path, 'rb') as f:
        while True:
            two_bytes = f.read(2)
            if not two_bytes:
                break
            data.append(scalar * int.from_bytes(two_bytes, byteorder='big'))
    return data


print(datfile_to_dict('./uploaded_files/846686373.bin'))
