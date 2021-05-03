import cb
import time

UART_SERVICE_UUID = '6E400001-B5A3-F393-E0A9-E50E24DCCA9E'
TX_CHAR_UUID      = '6E400002-B5A3-F393-E0A9-E50E24DCCA9E'
RX_CHAR_UUID      = '6E400003-B5A3-F393-E0A9-E50E24DCCA9E'
BLE_BLK_SZ        = 20

class PythonistaUartBleClient(object):
    def __init__(self, src_name, event_queue, ble_peripheral_name_preamble, buffer_obj, DEBUG=False):
        self.src_name = src_name
        self.event_queue = event_queue
        self.peripheral_name_preamble = ble_peripheral_name_preamble
        self.buffer_obj = buffer_obj
        self.DEBUG = DEBUG
        self.event = {}
        self.peripheral = None
        self.out_buffer = b''
        self.characteristics = False

    def did_discover_peripheral(self, p):
        self.event = {'src':self.src_name, 'ok':True, 
                        'status':'STATUS_DISCOVERED_PERIPHERAL',  
                        'resp':{'peripheral':p.name}
                        }
        if p.name and self.DEBUG: self.event_queue.append(self.event)
        if p.name and self.peripheral_name_preamble in p.name and not self.peripheral:
            self.peripheral = p
            cb.connect_peripheral(p)

    def did_connect_peripheral(self, p):
        self.event = {'src':self.src_name, 'ok':True, 
                        'status':'STATUS_CONNECTED_TO_PERIPHERAL',  
                        'resp':{'peripheral':p.name}
                        }
        self.event_queue.append(self.event)
        p.discover_services()

    def did_fail_to_connect_peripheral(self, p, error):
        self.event = {'src':self.src_name, 'ok':False, 
                        'status':'ERROR_FAILED_TO_CONNECT_TO_PERIPHERAL',  
                        'resp':{'error':error}
                        }
        self.event_queue.append(self.event)

    def did_disconnect_peripheral(self, p, error):
        print("disconnected")
        self.event = {'src':self.src_name, 'ok':True, 
                        'status':'STATUS_DISCONNECTED_FROM_PERIPHERAL',  
                        'resp':{'peripheral':p.name, 'error':error}
                        }
        self.event_queue.append(self.event)
        self.peripheral = None
        if self.buffer_obj.logging:
            self.buffer_obj.logging = False
            self.buffer_obj.logfile.close()
            print("CLOSED LOGFILE")
            self.event = {'src':self.src_name, 'ok': False, 'status': 'DISCONNECTED_AND_CLOSED_LOG',
                          'resp': {'peripheral': p.name, 'error': error}}
            self.event_queue.append(self.event)
        time.sleep(0.5)
        cb.scan_for_peripherals()

    def did_discover_services(self, p, error):
        for s in p.services:
            if s.uuid == UART_SERVICE_UUID:
                self.event = {'src':self.src_name, 'ok':True, 
                        'status':'STATUS_DISCOVERED_SERVICES',  
                        'resp':{'peripheral':p.name, 'service':'UART_SERVICE'}
                        }
                self.event_queue.append(self.event)
                p.discover_characteristics(s)
                cb.stop_scan()

    def did_discover_characteristics(self, s, error):
        self.event = {'src':self.src_name, 'ok':True, 
                        'status':'STATUS_DISCOVERED_CHARACTERISTICS',  
                        'resp':{'characteristics':[]}
                        }           
        for c in s.characteristics:
            if TX_CHAR_UUID in c.uuid:
                self.event['resp']['characteristics'].append('TX_CHAR')
                self.data_char = c
            elif RX_CHAR_UUID in c.uuid:
                self.event['resp']['characteristics'].append('RX_CHAR')
                self.peripheral.set_notify_value(c, True)
            else:
                self.event['ok'] = False
                self.event['status'] = 'ERROR_UNEXPECTED_SERVICE'
        self.event_queue.append(self.event)
        self.characteristics = True
              
    def did_update_value(self, c, error):
        self.buffer_obj.buffer(c.value)

    def did_write_value(self, c, error):
        if self.peripheral and self.out_buffer:
            if len(self.out_buffer) and ( len(self.out_buffer) <= BLE_BLK_SZ ):
                self.peripheral.write_characteristic_value(self.data_char, self.out_buffer, True)
                self.out_buffer = b''
            else:
                self.peripheral.write_characteristic_value(self.data_char, self.out_buffer[0:BLE_BLK_SZ], True)
                self.out_buffer = self.out_buffer[BLE_BLK_SZ:]
    
    def flush(self):
        self.in_buffer = b''

    def in_waiting(self):
        return(len(self.in_buffer))

    def write(self, cmd):
        if self.peripheral:
            if cmd:
                self.peripheral.write_characteristic_value(self.data_char, cmd[0:BLE_BLK_SZ], True)
                self.out_buffer = cmd[BLE_BLK_SZ:]
