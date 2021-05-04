# Python imports
import ui
import os
import json
import textwrap
import shutil
from collections import defaultdict
import time
import datetime as datetime
from pytz import timezone


# Pythonista imports
import cb
import console
import Image

# Metre imports
from lib.ParamsDb import ParamsDb
from lib.ViewListView import ViewListView
from lib.LineBuffer import LineBuffer
from lib.PythonistaUartBleClient import PythonistaUartBleClient
from lib.FileConverter import FileConverter
from lib.UIFeatures import ConsoleAlert

# Global constants



class BleUploader():
    def __init__(self, progress_bar_, console_box_, ble_status_icon_, v_, version_id, debug_status):
        self.progress_bar_ = progress_bar_
        self.console_box_ = console_box_
        self.ble_status_icon_ = ble_status_icon_
        self.v_ = v_
        self.version_id = version_id
        self.POPOVER_WIDTH = 500
        self.SEND_TEXT_VIEW_HEIGHT = 30
        self.POPOVER_DIALOG_NAME = 'km_ble_test.py'
        self.PERIPHERAL_PREAMBLE = 'CIRCUITPY'
        self.DEBUG = False
        self.CONSOLE_WIDTH = 140
        self.INDENT_STR = '        '
        self.DEBUG = debug_status
        
        self.instr_icon = self.v_['imageview']
        self.d0 = self.v_['dot0']
        self.d1 = self.v_['dot1']
        self.d2 = self.v_['dot2']
        self.d3 = self.v_['dot3']
        self.d4 = self.v_['dot4']
        
        # Global variables
        self.in_buf =b''
        self.cwd = os.getcwd()
        
        try:
            self.base_dir = self.cwd
            os.listdir(self.base_dir + '/data_files/uploaded_files')
               
        except:
            self.base_dir = self.cwd + '/MetreiOS/MetreAppUI_' + self.version_id 
            os.listdir(self.base_dir + '/data_files/uploaded_files') 
        

        
        self.event_queue = []
        self.py_ble_buffer = LineBuffer('py_ble', self.event_queue,   log_path_name=self.base_dir +'/data_files/dat_files/', DEBUG=self.DEBUG)
        # Initialize Bluetoooth
        self.py_ble_uart = PythonistaUartBleClient('py_ble', self.event_queue,    self.PERIPHERAL_PREAMBLE, self.py_ble_buffer, DEBUG=self.DEBUG)
        
    def print_wrap(self, text, indent_str, len):
        if self.DEBUG:
            lines = textwrap.wrap(text, width=len, subsequent_indent=indent_str)
            for line in lines:
                print(line)

    def blink(self):        
        if self.d0.alpha == 0.5:
            self.d1.alpha= 0.5
            self.d2.alpha= 0
            self.d3.alpha= 0
            self.d4.alpha= 0
            self.d0.alpha= 0
        elif self.d1.alpha == 0.5:
            self.d2.alpha=  0.5
            self.d3.alpha=  0
            self.d4.alpha= 0
            self.d0.alpha=  0
            self.d1.alpha=  0
        elif self.d2.alpha == 0.5:
            self.d3.alpha=  0.5
            self.d4.alpha= 0
            self.d0.alpha=  0
            self.d1.alpha=  0
            self.d2.alpha=  0
        elif self.d3.alpha == 0.5:
            self.d4.alpha=  0.5
            self.d0.alpha= 0
            self.d1.alpha=  0
            self.d2.alpha=  0
            self.d3.alpha=  0         
        elif self.d4.alpha == 0.5:
            self.d0.alpha=  0.5
            self.d1.alpha= 0
            self.d2.alpha=  0
            self.d3.alpha=  0
            self.d4.alpha=  0


    def blink_dev(self):
        if self.instr_icon.alpha == 0.25:
            self.instr_icon.alpha = 0.5
        elif self.instr_icon.alpha == 0.5:
            self.instr_icon.alpha = 0.25
    
    def execute_transfer(self):
        global in_buf
        in_buf = b''
        
        cb.reset()
        cb.set_central_delegate(self.py_ble_uart)
        cb.scan_for_peripherals()
        self.event_queue.append({'src':'py_ble', 'ack':'cb', 'ok':True,  'status':'STATUS_BLE_SCANNING_FOR_PERIPHERALS'})
        self.progress_bar_.update_progress_bar(0)
        while not self.py_ble_uart.peripheral:
            if len(self.event_queue):
                event = self.event_queue.pop()
                if self.DEBUG:
                    print(f"event: {event}")
        if self.py_ble_uart.peripheral:
            self.console_box_.alpha =1
            self.console_box_.text = ("Connecting to MetreAce instrument")
            #dev_icon_path = 'images/MetreAceDev.png'
            self.d0.alpha = 0.5
            #self.instr_icon.image = ui.Image.named(dev_icon_path)
            self.instr_icon.alpha = 0.25
            
            
        def is_dst(dt=None, tzone="UTC"):
            if dt is None:
                dt = datetime.datetime.utcnow()
            t_zone = timezone(tzone)
            timezone_aware_date = t_zone.localize(dt, is_dst=None)
            return timezone_aware_date.tzinfo._dst.seconds
        
        def calc_utc_offset(timeval):
            tz_dict = {"US/Eastern": 5,
            "US/Central": 6,
            "US/Mountain": 7,
            "US/Pacific": 8,
            "US/Alaska": 9,
            "US/Hawaii": 10,
            }
            try:
                with open('log/timezone_settings.json') as f:
                    tzsource = json.loads(f)
                    tz = tzsource['timezone']
            except:
                tz = 'US/Pacific'
            dt1 = datetime.datetime.fromtimestamp(timeval).astimezone(timezone(tz))
            dst_term_sec = is_dst(datetime.datetime(int(dt1.year), int(dt1.month), int(dt1.day)), tzone="US/Pacific")
            tz_factor = int(tz_dict[tz]) - dst_term_sec/3600
            return int(tz_factor)
        
                    
        def cmd_fn(out_msg, cmd_type, show_progress = False, cmd_counter = 0, to_counter = 0, warning = False, to_max = 80):
            global in_buf
            in_buf = (out_msg + '\n').encode('utf-8')
            
            while True:
                
                if self.py_ble_uart.peripheral:
                    
                    #ui.animate(self.blink, 0.1)
                
                    try:  
                        #ui.animate(self.blink, 0.1)
                        if show_progress:
                            if self.progress_bar_.fillbar_.width < 0.8:
                                self.progress_bar_.update_progress_bar(cmd_counter*.005)
                                ui.animate(self.blink,0.1)
                            else:
                                self.progress_bar_.update_progress_bar(cmd_counter*.0025)

                    # Sends commands to buffer
                        if len(in_buf):
                            if self.DEBUG:
                                print('the length of in_buff is ', len(in_buf))
                            in_chars = in_buf
                            self.py_ble_buffer.buffer(in_chars)
                            in_buf = ''
                        # if events then process them
                        while len(self.event_queue) and self.py_ble_uart.peripheral:
                            if self.DEBUG:
                                print('processing events')
                            event = self.event_queue.pop()
                         
                            if 'post' in event:
                                response = json.loads(event['post'])
                                if 'cmd' in response:
                                    try:
                                        self.py_ble_uart.write((event    ['post']+'\n').encode())
                                                            # print(f"event: {event}")
                                        self.print_wrap(f"event: {event}",   self.INDENT_STR, self.CONSOLE_WIDTH)
                                        if self.DEBUG:
                                            print('sent a post cmd')
                                        
                                        continue
                                    except:
                                        resp_string = "Connecting"
                                        break
            
                                else:
                    
                                    if self.DEBUG:
                                        print('cmd not in post')
                                    try:
                                        if self.DEBUG:
                                            print('printing event response')
                                        self.print_wrap(f"event: {response}",    self.INDENT_STR, self.CONSOLE_WIDTH)
                                        if cmd_type in response['ack']:
                                            return response['resp'], cmd_counter
                                        else:
                                            continue
                                    except:
                                        if self.DEBUG:
                                            print('could not get event response')
                                        continue
                            else:
                                if self.DEBUG:
                                    print('No post in event')
                                self.print_wrap(f"event: {event}", self.INDENT_STR,   self.CONSOLE_WIDTH)
            
                        
                    except KeyboardInterrupt as e:
                        cb.reset()
                        print(f"Ctrl-C Exiting: {e}")
                        break
                    time.sleep(0.2)
                    ui.animate(self.blink, 0.1)
                    cmd_counter = cmd_counter + 1
                    to_counter = to_counter + 1
                    if self.DEBUG:
                        print('cmd_counter', cmd_counter)
                    if warning and to_counter > to_max:
                        self.console_box_.text = "Ooops. MetreAce needs to be restarted. \n Eject mouthpiece, close the phone app, and try again"
                        break
                    
                else:
                    resp_string = "NOT connected"
                    return resp_string, cmd_counter
    
            
        time.sleep(2)
        if self.py_ble_uart.peripheral:
            print('this is what alpha d0 is ' + str(self.d0.alpha))
            self.v_['ble_status'].text = 'Connected'
            self.console_box_.text = "Connected"
            self.d0.alpha = 0.5
            if self.DEBUG:
                print('will be using ' + self.cwd + '/data_files/dat_files/ as current working directory for writing log files')
            global counter
            counter = 0
            time.sleep(0.2)
            connect_msg_txt =json.dumps({"cmd":"set_ble_state","active":True})
            cmd_fn(connect_msg_txt, "set_ble_state", show_progress = False)

            ble_icon_path = 'images/ble_connected.png'
            self.ble_status_icon_.image = ui.Image.named(ble_icon_path)
            self.ble_status_icon_.background_color = "white"
        
        
            #### Set the time and timezone offset (account for DST)
            time.sleep(0.2)
            current_time = int(time.time())
            
            out_msg00 =json.dumps({"cmd": "set_time","time": str(current_time)})
            r00, no_counter = cmd_fn(out_msg00, "set_time")
            
            # Here is command to set timezone/DST
            offset_hrs = calc_utc_offset(current_time)
            time.sleep(2)
            out_msg0 =json.dumps({"cmd": "set_time_offset","offset": str(offset_hrs)})
            r0, no_counter = cmd_fn(out_msg0, "set_time_offset")
            

            time.sleep(0.5)
            out_msg1 =json.dumps({"cmd": "listdir","path": "/sd"})
            try:
                r1, no_counter = cmd_fn(out_msg1, "listdir",  warning = True, to_max = 120)
                list_of_dirs = r1['dir']
                file_sizes = r1['stat']
            except:
                 ConsoleAlert('Connection Error! Remove Mouthpiece, Close App, Try Again!', self.v_)
                 ble_icon_path = 'images/ble_off.png'
                 self.ble_status_icon_.image = ui.Image.named(ble_icon_path)
                 self.ble_status_icon_.background_color = 'black'
                 #out_msg2 =json.dumps({"cmd": "disconnect_ble"})
                 #rstring, no_counter = cmd_fn(out_msg2)
                 return False
            self.console_box_.text = str(list_of_dirs)

            file_list = []
            for file in list_of_dirs:
                if file.startswith('.'):
                    continue
                elif file.endswith('.bin'):
                    file_list.append(file)
              
        # HAVE A MESSAGE IF NO FILES READY TO BE UPLOADED
            self.ble_status_icon_.background_color = 'orange'
            self.v_['ble_status'].alpha = 0.5
            self.console_box_.text = 'Found ' + str(len(file_list)) + ' test files on your MetreAce'
            time.sleep(0.5)
            
            out_msg_text =json.dumps({"cmd":"oled", "text":"Uploading..."})
            cmd_fn(out_msg_text, "oled", show_progress = False, warning = True)
                                      
            FLAG = False
            file_wrongsize = []
            first_alert = True
            for file in list_of_dirs:
                
                timeout_counter = 1
                if file.startswith('._'):
                    if self.DEBUG:
                        print('I SEE ' + file)
                    out_msg_del_e =json.dumps({"cmd": "remove", "path":     "/sd/" + file})
                    r_del, counter = cmd_fn(out_msg_del_e, "remove", show_progress = False, warning = True, to_max = 150)
                elif file.endswith(('.bin', '.json')):
                    if "device" in file:
                        if self.DEBUG:
                            print('I SEE ' + file)
                            print('Skipping over ' + file)
                        continue
                    elif "params" in file:
                        if self.DEBUG:
                            print('I SEE ' + file)
                            print('Skipping over ' + file)
                        continue
                    else:
                        if self.DEBUG:
                            print('I SEE ' + file)
                        file_ix = list_of_dirs.index(file)
                        file_size = file_sizes[file_ix]
                        try:
                            self.console_box_.text =  'Fetching ' + str(file_list.index(file) + 1) + ' out of ' + str(len(file_list)) + ' test files from your MetreAce'
                        except:
                            pass
                        if file.endswith('.bin'):
                            counter = 1
                        filename, ext = file.split('.')
                        if int(filename) < 1614306565 and first_alert:
                            ConsoleAlert('Warning: May need to replace clock battery!', self.v_)
                            first_alert = False
                        
                        out_msg =json.dumps({"cmd": "ble_get_file", "path":     "/sd/" + file})
                        in_buf = (out_msg + '\n').encode('utf-8')
                        result_resp = []
                        while self.py_ble_uart.peripheral:
                            try:
                                if self.progress_bar_.fillbar_.width < 0.8:
                                    self.progress_bar_.update_progress_bar(counter*.005)
                                else:
                                    self.progress_bar_.update_progress_bar(counter*.0025)
                                if len(in_buf):
                                    in_chars = in_buf
                                    self.py_ble_buffer.buffer(in_chars)
                                    in_buf = ''
                                if len(self.event_queue):
                                    event = self.event_queue.pop()

                                    if 'post' in event:
                                        try:
                                            response = json.loads(event['post'])
                                            if 'cmd' in response:
                                                self.py_ble_uart.write((event    ['post']+'\n').encode())
                                                self.print_wrap(f"cmd_event: {event}",   self.INDENT_STR, self.CONSOLE_WIDTH)
                                            else:
                                                self.print_wrap(f"no_cmd_event: {response}",    self.INDENT_STR, self.CONSOLE_WIDTH)
                                                if response['ok']:
                                                    try:
                                                         result_resp.append(str(response['resp']))
                                                         self.print_wrap(f"resp_event: {response}",   self.INDENT_STR, self.CONSOLE_WIDTH)
                                                    except:
                                                        result_resp.append(str(response['ack']))
                                                        self.print_wrap(f"ack_event: {response}",   self.INDENT_STR, self.CONSOLE_WIDTH)
                                                else:
                                                    if self.DEBUG:
                                                        print("RESPONSE IS NOT OKAY")
                                                    break
                                        except:
                                            pass
    
                                    else:
                                        if self.DEBUG:
                                            print(str(event))
                                        #response = json.loads(str(event))
                                        if event['ok']:
                                           self.print_wrap(f"event: {event}",   self.INDENT_STR, self.CONSOLE_WIDTH)
                                           pass
                                        else:
                                           FLAG = True
                                           self.print_wrap(f"event: {event}",    self.INDENT_STR, self.CONSOLE_WIDTH)
                                           break
                                        
                                time.sleep(0.2)
                                ui.animate(self.blink, 0.1)
                                counter = counter + 1
                                timeout_counter = timeout_counter + 1
                                if timeout_counter > 2000:
                                    self.console_box_.text = "One of your tests could not be processed"
                                    break
                                
                            except KeyboardInterrupt as e:
                                cb.reset()
                                print(f"Ctrl-C Exiting: {e}")
                                break
                           
                            if "{'file_path': './result.bin'}" in result_resp:
                                if self.DEBUG:
                                    print('ENTERING TRANSFER AND REMOVAL ATTEMPT')
                               
                                try:
                                    shutil.move('./result.bin', self.base_dir + '/data_files/uploaded_files/' + file)
                                    upload_size = os.stat(self.base_dir + '/data_files/uploaded_files/' + file)[6]
                                    if self.DEBUG:
                                        print('Sent move command')
                                    if upload_size == file_size:
                                        if self.DEBUG:
                                            print('upload and file size are the same size')
                                        out_msg_del =json.dumps({"cmd": "remove", "path":"/sd/" + file})
                                        r_del, counter = cmd_fn(out_msg_del, "remove", show_progress = True, cmd_counter = counter, warning = True)  
                                        if self.DEBUG:
                                            print('Sent remove command here')
                                    else:
                                        if self.DEBUG:
                                            print('FILE IS THE WRONG SIZE')
                                        size_diff = file_size - upload_size
                                        file_wrongsize.append(file)
                                        file_wrongsize.append(size_diff)
                                        out_msg_del =json.dumps({"cmd": "remove", "path":"/sd/" + file})
                                        r_del, counter = cmd_fn(out_msg_del, "remove", show_progress = True, cmd_counter = counter, warning = True)
                                    
                                    if file.endswith('bin'):
                                        counter = counter + 1
                                        self.progress_bar_.update_progress_bar(counter*.002)
                                        break 
                                        # No break and no continue makes it exit and not remove the bin file
                                    elif file.endswith('json'):
                                        pass
                                        
                                except:
                                    if self.DEBUG:
                                        print('BROKE OUT OF TRANSFER AND REMOVAL ATTEMPT')
                                    break
                        if FLAG:
                           counter = 0
                           cb.reset()
                           return False
                       
                else:
                    continue
            # Now use FileConverter
            fc = FileConverter(self.progress_bar_, self.console_box_, file_wrongsize)
            cwd = os.getcwd()
            if self.DEBUG:
                print('THIS IS THE CURRENT DIR: ' + cwd)
                print('THIS IS SELF.BASEDIR: ' + self.base_dir)

            conversion_status = fc.match_files(self.base_dir + '/data_files/uploaded_files', self.base_dir + '/data_files/processed_files', self.base_dir + '/data_files/converted_files', self.base_dir + '/data_files/unpaired_files')
            self.console_box_.text = 'Transfer of ' + str(len(file_list)) + ' out of ' + str(len(file_list)) + ' test files complete'
            self.progress_bar_.update_progress_bar(1)
            self.ble_status_icon_.background_color = 'white'
            self.v_['ble_status'].text = ''
            self.d0.alpha =  0
            self.d1.alpha =  0
            self.d2.alpha =  0
            self.d3.alpha =  0
            self.d4.alpha =  0

            self.instr_icon.alpha = 0.1
            
            try:
                out_msg_txt =json.dumps({"cmd":"set_ble_state","active":False})
                cmd_fn(out_msg_txt, "set_ble_state", show_progress = False, to_max = 50)
            except:
                if self.DEBUG:
                    print('could not send disconnect command')


                                     
            self.console_box_.text = 'Disconnecting from MetreAce Instrument'
            
            try:          
                out_msg2 =json.dumps({"cmd": "disconnect_ble"})
                rstring, no_counter = cmd_fn(out_msg2, "disconnect_ble", show_progress = True, to_max = 30)
            except:
                if self.DEBUG:
                    print('could not send disconnect command')
            ConsoleAlert('Remove Mouthpiece!', self.v_)
            ble_icon_path = 'images/ble_off.png'
            self.ble_status_icon_.image = ui.Image.named(ble_icon_path)
            self.ble_status_icon_.background_color = 'black'
            return conversion_status
