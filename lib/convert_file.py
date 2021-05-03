import json
from lib.ycoding import yencode, ydecode
from lib.crc16pure import crc16xmodem

def convert_file(event):
    line_num = 0
    event['ack'] = event['cmd']
    event['cmd'] = 'log_event'
    bad_crcs=[]
    try:
        if event['targ_path'] != '':
            with open(event['dest_path'], 'wb') as out_file:
                with open(event['targ_path'], 'rb') as f:
                    while True:
                        f_line = f.readline()
                        if not f_line:
                            break
                        # print(f"f_line: {f_line}")
                        chunk_bytes = ydecode(f_line[1:-1])
                        # print(f"chunk_bytes: {hexlify(chunk_bytes, ' ')}")
                        shipped_crc = chunk_bytes[-2:]
                        chunk_bytes = chunk_bytes[:-2]
                        # print(f"shipped_crc: {hexlify(shipped_crc, ' ')}")
                        # print(hexlify(chunk_bytes, ' '))
                        calculated_crc = crc16xmodem(chunk_bytes).to_bytes(2, 'big')
                        # print(calculated_crc)
                        if not (shipped_crc == calculated_crc):
                            print('.')
                            bad_crcs.append(line_num)
                            crc_OK = False
                            out_file.write((FILE_CHUNK_SIZE * DATA_LEN * chr(0)).encode('utf_8'))
                        else:
                            out_file.write(chunk_bytes)
                        line_num += 1
                        event['ok'] = True
    except OSError as e:
        event['status'] = 'ERR_OSError'
        event['status_cmd'] = e
        event['ok'] = False
    return event

if __name__ == '__main__':
    foo = '{"cmd":"convert_file","targ_path":"log-1613521786.dat", "dest_path":"test.bin"}'
    event=json.loads(foo)
    convert_file(event)
