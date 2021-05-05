DEBUG = False

## Python imports
import os
import requests
import shutil
import numpy as np
from io import BytesIO
import datetime as datetime
import time
from pytz import timezone
import json
import threading
import fnmatch
import pprint
import math
from functools import partial
import itertools
import matplotlib.pyplot as plt
from matplotlib.dates import num2date, date2num, num2epoch

# Pythonista imports
import ui
import Image
import console
from objc_util import on_main_thread


# Metre imports
import process_test
from ble_file_uploader import BleUploader
from lib.UISummaryDelegate import SummaryDelegate
from lib.UIBleDelegate import BleDelegate, BokehDelegate, loading_html, updating_html, nolog_html, getPlot
from lib.UIHelpDelegate import HelpDelegate
from lib.UIFeatures import ProgressBar, ConsoleAlert
from lib.UITableDelegate import ResultsTable
from app_single_launch import AppSingleLaunch

# Using single launch lock as suggested in
# https://forum.omz-software.com/topic/5440/prevent-duplicate-launch-from-shortcut/7

APP_VERSION = 'v0.19'



class MainView(ui.View):
    def __init__(self):
    #def __init__(self, app: AppSingleLaunch):
        #self.app = app
        self.name = "MetreAce Home"
        self.flex = 'WH'
        #self.tint_color = '#494949'
        self.background_color = 'black'
        
        # Setup of UI Features
        
        self.v = ui.load_view('mainview')
        self.v.frame = self.bounds
        self.v.flex = 'WH'
        
        # Console
        self.app_console = self.v['console']
        self.app_console.alpha = 0
       
        # Ble connection
        self.star_button = self.v['start_button']
        self.ble_icon = self.v['ble_icon']
        self.ble_status_icon = self.v['ble_status_icon']
        self.ble_status = self.v['ble_status']
        self.connect_button = self.v['connect_button']
        ble_icon_path = 'images/ble_off.png'
        self.ble_status_icon.image = ui.Image.named(ble_icon_path)
        
        # Set up icons
        self.instr_icon = self.v['imageview']
        dev_icon_path = 'images/MetreAceDev.png'
        self.instr_icon.image = ui.Image.named(dev_icon_path)
        self.calc_icon = self.v['button1']
                
        # Status bar
        self.fillbar = self.v['fill_bar']
        self.fillbar_outline = self.v['background']
        # self.fillbar.x = 31.1
        self.fullbar = self.fillbar_outline.width

        # Instr chevrons
        self.d0 = self.v['dot0']
        self.d1 = self.v['dot1']
        self.d2 = self.v['dot2']
        self.d3 = self.v['dot3']
        self.d4 = self.v['dot4']        
        
        # Cloud chevrons
        self.d5 = self.v['dot5']
        self.d6 = self.v['dot6']
        self.d7 = self.v['dot7']
        self.d8 = self.v['dot8']
        self.d9 = self.v['dot9']
        
        # Version label
        self.vlabel = self.v['vlabel']
        self.vlabel.text = APP_VERSION
        
        # Setup
        self.cwd = os.getcwd()
        on_main_thread(console.set_idle_timer_disabled)(True)
        
        
        root_dir, metre_dir = self.cwd.split('MetreiOS')
        if DEBUG:
            print('This is self.cwd: ' + self.cwd)
            print('This is root_dir: ' + root_dir)
            
        # Download Single Launch Lock if it's not already installed
        check_path = root_dir + 'site-packages/single_launch.lock'
        if os.path.exists(check_path):
            if DEBUG:
                print('single_launch.lock already exists')
            else:
                print('')
        else:
            shutil.copy(self.cwd + '/resources/single_launch.lock', check_path )
            if DEBUG:
                print('moved copy of single_launch.lock')
            else:
                print('')


        # Set up UI Functions
        self.getData()
        self.results_table = self.v['results_table']
        self.restable_inst = ResultsTable(self.v, self.results_table, self.acetone, self.etime)
        self.add_subview(self.v)
        
        # Implementation of navigation view/mainview
        self.l = self.create_l_buttonItems('Settings','|','Results','|', 'Help')
        self.left_button_items = self.l
        self.files_to_upload = os.listdir(self.cwd + '/data_files/converted_files/')

        # Process pre-uploaded tests (if available)

        
    def init_check(self):
        if DEBUG:
            print("this is the size of files to upload")
            print(len(self.files_to_upload))
        if len(self.files_to_upload) >=2:
            self.app_console.text = 'Beginning Upload'
            self.main()
            self.star_button.alpha = 0.5
            self.ble_status.text = ''
        else:
            self.ble_status.text = 'CONNECT'
            self.bleStatus()
            
    def will_close(self) -> None:
        self.app.will_close()

    # This sets up main navigation view

    def button_nav(self, sender):
        def connect(a,b):
            
            if sender.title == a:
                view_to_push = b
                pushed_view = ui.load_view(view_to_push)
                self.v.navigation_view.push_view(pushed_view)
                    
                if sender.title=='Settings':
                    settings_page = pushed_view['view1']
                    s_table=settings_page['tableview1']
                    d_table = settings_page['dt_table']
                    ble_delegate = BleDelegate(settings_page, s_table, d_table, self.cwd)
                    
                if sender.title=='Results':
                    results_page = pushed_view['bokeh_bg']
                    bview = ui.load_view('bokehview') 
                    bokeh_delegate = BokehDelegate(pushed_view['webview1'], self.cwd)

                if sender.title =='Help':
                    help_page = pushed_view['toolbarview']
                    hview = ui.load_view('toolbar')
                    inst_page = pushed_view['online_instructions']
                    qa_page = pushed_view['online_qa']
                    recover_page = pushed_view['recover_button']
                    help_delegate = HelpDelegate(hview, inst_page, qa_page, recover_page)

                    
        connect('Settings','file_view')
        connect('Help','toolbar')
        connect('Results','bokehview')


    def create_l_buttonItems(self, *buttons):
        items=[]
        for b in buttons:
            b=ui.ButtonItem(b)
            b.tint_color='#494949'
            b.action= self.button_nav
            items.append(b)
        return items

# This sets up the bluetooth upload
    @ui.in_background
    def bleStatus(self):
        self.progress_bar = ProgressBar(self.fillbar, self.fillbar_outline, self.fullbar)
        self.star_button.alpha = 0.5
        self.progress_bar.fillbar_outline_.alpha = 1
        self.fillbar.alpha = 1
        loaded = False
        self.connect_button.alpha = 0
        ble_icon_path = 'images/ble_disconnected.png'
        self.ble_status_icon.image = ui.Image.named(ble_icon_path)
    
        if not loaded:
            self.ble_status.text= 'Connecting...'
            ble_file_uploader = BleUploader(self.progress_bar, self.app_console, self.ble_status_icon, self.v, APP_VERSION, DEBUG)
            ready_status = ble_file_uploader.execute_transfer()
            
            if ready_status:
                done = True
                #self.star_button.alpha = 0.25
                self.ble_status.text = ''
                
                
                # HERE is where you trigger the main function (i.e. after the button is pushed)
                self.main()
                self.connect_button.alpha = 1
                return done
            else:
                self.app_console.text = 'No breath tests are ready to be processed'
                if ble_file_uploader.py_ble_uart.peripheral:
                    ble_file_uploader.py_ble_uart.peripheral = False
                    self.ble_icon_path = 'images/ble_off.png'
                    self.ble_status_icon.image = ui.Image.named(ble_icon_path)
                    self.ble_status.text= 'CONNECT'
                    self.startbutton.alpha = 1
                    self.progress_bar.fillbar_outline_.alpha = 0
                    self.fillbar.alpha = 0
                else:
                    if DEBUG:
                        print("UI senses it is disconnected")
                    time.sleep(0.5)
                    self.app_console.text = 'Bluetooth connection lost. Reinsert mouthpiece to try again'
                    ble_icon_path = 'images/ble_off.png'
                    self.ble_status_icon.image = ui.Image.named(ble_icon_path)
                    self.ble_status_icon.background_color = 'black'
                    self.ble_status.text= 'CONNECT'
                    self.star_button.alpha = 1
                    self.progress_bar.fillbar_outline_.alpha = 0
                    self.fillbar.alpha = 0
                    
                ### THIS IS WHERE YOU SHOULD GIVE THE OPTION TO CONNECT AGAIN
                self.d0.alpha = 0 
                self.d1.alpha = 0
                self.d2.alpha = 0
                self.d3.alpha = 0
                self.d4.alpha = 0                
                self.d5.alpha = 0 
                self.d6.alpha = 0
                self.d7.alpha = 0
                self.d8.alpha = 0
                self.d9.alpha = 0
                self.instr_icon.alpha = 0.1
                self.connect_button.action = self.bleStatus()
                self.connect_button.alpha =1
            
        else:
            self.ble_icon_path = 'images/ble_disconnected.png'
            ble_icon.image = ui.Image.named(ble_icon_path)
            return done
        
    
    def getData(self):
        
        with open(self.cwd + '/log/log_003.json') as json_file:
            self.log = json.load(json_file)
        self.etime = []
        self.weektime = []
        for val in self.log['Etime']:
                tval = datetime.datetime.fromtimestamp(int(val))
                year, weeknum = tval.strftime("%Y-%U").split('-')
                weekcalc = str(year) + '-W' + str(weeknum)
                day_of_week = datetime.datetime.strptime(weekcalc + '-1', "%Y-W%W-%w")
                self.weektime.append(day_of_week)
                self.etime.append(tval)
        self.acetone = np.array(self.log['Acetone'])
        dtDateTime = []
        for i in range(0, len(self.log['DateTime'])):
            dtDateTime.append(datetime.datetime.strptime(self.log['DateTime'][i], '%Y-%m-%d %H:%M:%S'))
        vectorized = []
    
        for i in range(0, len(self.acetone)):
                vectorized.append([self.weektime[i], self.acetone[i], dtDateTime[i]])
                self.varray = np.array(vectorized)
        if len(self.acetone) <=0:
            self.varray = []
        
    ########################################
    def blink(self):     
        if self.d5.alpha == 0.5:
            self.d6.alpha= 0.5
            self.d7.alpha= 0
            self.d8.alpha= 0
            self.d9.alpha= 0
            self.d5.alpha= 0
        elif self.d6.alpha == 0.5:
            self.d7.alpha=  0.5
            self.d8.alpha=  0
            self.d9.alpha= 0
            self.d5.alpha=  0
            self.d6.alpha=  0
        elif self.d7.alpha == 0.5:
            self.d8.alpha=  0.5
            self.d9.alpha= 0
            self.d5.alpha=  0
            self.d6.alpha=  0
            self.d7.alpha=  0
        elif self.d8.alpha == 0.5:
            self.d9.alpha=  0.5
            self.d5.alpha= 0
            self.d6.alpha=  0
            self.d7.alpha=  0
            self.d8.alpha=  0         
        elif self.d9.alpha == 0.5:
            self.d5.alpha=  0.5
            self.d6.alpha= 0
            self.d7.alpha=  0
            self.d8.alpha=  0
            self.d9.alpha=  0    
    
    def main(self):
        self.ble_status.alpha = 0.5 
        self.calc_icon.apha = 0.1
        self.main_progress_bar =ProgressBar(self.fillbar, self.fillbar_outline, self.fullbar)
        global process_done
        process_done = False
        
        def animate_bar():
            cloud_progress_bar = ProgressBar(self.fillbar, self.fillbar_outline, self.fullbar)
            for i in range(0, 200):
                if process_done:
                    break
                cloud_progress_bar.update_progress_bar(0.002*i + 0.15)
                ui.animate(self.blink, 0.1)
                if DEBUG: print(i)
                time.sleep(0.2)

    
        source_path = self.cwd + '/data_files/converted_files/'
        all_src_files = os.listdir(source_path)
        files = []
        for file in all_src_files:
            if ".gitkeep" not in file:
                files.append(file)
        if DEBUG:
            print("these are the files in converted_files: " + str(files))
        numOfFiles = len(files)
        self.app_console.alpha = 1
        if numOfFiles >1:
            self.app_console.text = str(numOfFiles-1) + ' breath tests are ready to be processed. Beginning data processing...'
            self.d5.alpha = 0.5
        elif numOfFiles == 1:
            self.app_console.text = '1 breath test is ready to be processed. Beginning data processing...'
            self.d5.alpha = 0.5
        else:
            self.app_console.text = 'No breath tests are ready to be processed at this time'
        time.sleep(3)
        
        try:
            with open(self.cwd + '/log/timezone_settings.json') as f:
                tzsource = json.loads(f)
                tz = 'US/Pacific'
        
        
        except:
                tz = 'US/Pacific'
        
        for file in files:
               if fnmatch.fnmatch(file, '*.json'):

                   dt = datetime.datetime.fromtimestamp(int(file.split('-')[0])).astimezone(timezone(tz)).strftime('%b %d, %Y, %I:%M %p')
                   ui.animate(self.blink, 0.1)
                   if DEBUG:
                       print('Beginning Analysis of test from ' + dt)
                   json_path = source_path + '/'+ file
                   self.main_progress_bar.update_progress_bar(0)
                   process_done = False
                   with open(json_path) as f:
                       data_dict = json.load(f)
                   try:
                       data_dict_to_send = process_test.process(data_dict, dt, DEBUG)
                       url = 'https://us-central1-metre3-1600021174892.cloudfunctions.net/metre-7500'
                       data_dict_to_send['App_Version'] = APP_VERSION
                       json_text = json.dumps(data_dict_to_send)
                       self.main_progress_bar.update_progress_bar(0.1)
                       self.app_console.text = 'Uploading and interpreting results from test from your ' + dt +' test. This may take a few moments...'
                       pt = threading.Thread(target = animate_bar) # don't do this unless u start a parallel thread to send request
                       pt.start()
                       if DEBUG:
                           print('sending to cloud')
                       start = time.time()
                       response = requests.post(url, files = [('json_file', ('test.json', json_text, 'application/json'))])
                       process_done = True
                       elapsedtime = time.time()-start
                       if DEBUG: 
                           print('received response--response time ' + str(elapsedtime))
                       response_json = json.loads(response.text)
                       pt.join()
                       process_done = True
                       
                       self.app_console.text = 'Results from ' + dt + ': ' + response_json['pred_content']
                       if DEBUG:
                            print(response_json['pred_content'])
                       self.main_progress_bar.update_progress_bar(0.92)
                       newlog = {'Etime': response_json['refnum'],
                                  'DateTime': response_json['DateTime'],
                                  'Acetone': float(response_json['Acetone']),
                                  'Sensor': response_json['sensor'],
                                  'Instr': response_json['instrument']}
                       for key, value in self.log.items():
                          self.log[key].append(newlog[key])
                       with open(self.cwd + "/log/log_003.json", "w") as outfile:
                          json.dump(self.log, outfile)
                       self.getData()
                       if DEBUG:
                            print(self.acetone)
                       self.main_progress_bar.update_progress_bar(0.95)
                       self.results_table = self.v['results_table']
                       self.restable_inst.update_table(self.acetone, self.etime)                        
                       self.main_progress_bar.update_progress_bar(1)
                   except:
                       self.app_console.text = 'The test from ' + dt + ' could not be processed.'
                       time.sleep(1)
                   shutil.move(source_path + file, self.cwd +'/data_files/processed_files/' + file)
               else:
                   continue
               time.sleep(1)
        self.getData()
        self.restable_inst.update_table(self.acetone, self.etime)                                     
        self.fillbar.alpha =0
        self.fillbar_outline.alpha = 0
        self.main_progress_bar.update_progress_bar(0)
        self.d5.alpha = 0
        self.d6.alpha = 0
        self.d7.alpha = 0
        self.d8.alpha = 0
        self.d9.alpha = 0
        self.calc_icon.alpha = 0.1
                                            
        self.app_console.text = 'Test Processing and Upload Complete.'
        time.sleep(3)
        self.app_console.alpha = 0
        self.app_console.text = ''
        #self.star_button.alpha = 1
        self.connect_button.action = self.bleStatus()
        self.ble_status.alpha = 1
        
        #self.ble_status.text = 'CONNECT'


class NavView(ui.View):
    def __init__(self, app: AppSingleLaunch):
        self.app = app
        self.tint_color =  '#494949'  
        self.name = "MetreAce Nav"
        self.flex = 'WH'
        self.mainscript = MainView()
        self.nav = ui.NavigationView(self.mainscript)

        

if __name__ == '__main__':
    app = AppSingleLaunch("MetreAce Nav")
    if not app.is_active():
        nav_class = NavView(app)
        nav_view = nav_class.nav
        nav_view.tint_color =  '#494949'                                   
        app.will_present(nav_view)
        nav_view.present()
        nav_class.mainscript.init_check()
        self.connect_button.action = self.bleStatus()
        self.ble_status.alpha = 1
