import time
import json
from binascii import hexlify

from lib.convert_file import convert_file

class LineBuffer():
    def __init__(self, buffer_name, event_queue, log_path_name='', DEBUG=False):
        self.buffer_name = buffer_name
        self.event_queue = event_queue
        self.fn_dict = {
                'D' : self.log,
                'E' : self.end_log
                }
        self.log_path_name = log_path_name
        self.DEBUG = DEBUG
        self.in_buffer = b''
        self.logfile_path = None
        self.logfile = None
        self.logging = False
        self.then = time.monotonic()
        self.line_index = 0
        self.first = True

    def __exit__(self, *args):
        if self.logfile: 
            self.logfile.close()
        self.delta_t = time.monotonic() - self.then

    def log(self, line):
        if not self.logging:
            self.logging = True
            self.logfile_path = self.log_path_name + "log-" + f"{int(time.time())}" + ".dat"
            self.logfile = open(self.logfile_path, 'wb')
            event = {'post':json.dumps({'src':self.buffer_name, 'ack':'log', 'ok':True, 'resp':{'file_path':self.logfile_path}})}
            self.event_queue.append(event)
        # print(hexlify(line + b'\n'))
        if self.DEBUG:
            print('.', end='')
        self.logfile.write(line + b'\n')

    def end_log(self, line):
        if self.logging:
            self.logging = False
            self.logfile.close()
            event={"cmd":"convert_file","targ_path":self.logfile_path, "dest_path":"./result.bin"}
            result = convert_file(event)
            if result['ok']:
                event = {'post':json.dumps({'src':self.buffer_name, 'ack':'end_log', 'ok':True, 'resp':{'file_path':result['dest_path']}})}
            else:
                event = result
            self.event_queue.append(event)
            self.logfile_path = None

    def post(self, line):
        # print('.',end='')
        event = {'src':self.buffer_name, 'ok':True,'post':line.decode(), 'n':self.line_index}
        self.event_queue.append(event)
        self.line_index += 1

    def buffer(self, in_bytes):
        lines = []
        try:
            if self.first:
                self.then = time.monotonic()
                self.first = False
            self.in_buffer += in_bytes
            if self.DEBUG: print(self.in_buffer)
            lines = (self.in_buffer).splitlines()
            if len(lines):
                if not in_bytes.endswith(b'\n') or lines[-1] == b'':
                    self.in_buffer = lines[-1]
                    lines.pop()
                else:
                    self.in_buffer = b''
            if self.DEBUG: print(lines)
            while len(lines):
                line = lines.pop(0)
                func = self.fn_dict.get(chr(line[0]), self.post)
                func(line)
        except Exception as e:
            self.event_queue.append({'post':{ 'src':self.buffer_name, 'ack':'buffer', 'ok':False, 
                                      'resp':{'exception':e, 'in_bytes':in_bytes, 'in_buffer': self.in_buffer, 'lines':lines}
                                    }})
