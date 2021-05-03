# Python imports
import requests
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

# Pythonista imports
import ui
import Image

loading_html = '''
<html>
<head>
<body>
<h1> Loading Previous Results... <h1>
</body>
</html>
'''

updating_html = '''
<html>
<head>
<body>
<h1> Updating Chart... <h1>
</body>
</html>
'''


nolog_html = '''
<html>
<head>
<body>
<h1> Your test results will show up here once processed <h1>
</body>
</html>
'''

def getPlot(bview, src, initial = True):
    
    try:
        url = 'https://us-central1-metre3-1600021174892.cloudfunctions.net/metre-3'
        if initial:
            bview.load_html(loading_html)
        else:
            bview.load_html(updating_html)
        with open(src + '/log/log_003.json') as json_file:
            log = json.load(json_file)
        logData = json.dumps(log)
        try:
            tzData = json.loads(src + '/log/timezone_settings.json')
        except:
            tzData = json.dumps({'timezone': 'US/Pacific'})
        response = requests.post(url, files = [('json_file', ('log.json', logData, 'application/json')), ('tz_info', ('tz.json', tzData, 'application/json'))])
        
        bview.load_html(response.text)
        
    # Handles exception if no previous log data
    except:
        bview.load_html(nolog_html)
        
class BokehDelegate(object):
    def __init__(self, subview_, cwd_):
        self.subview = subview_
        self.cwd = cwd_
        getPlot(self.subview, self.cwd)

        
        
class BleDelegate(object):
	def __init__(self, subview_, table_, dt_table_, cwd_):
		self.subview = subview_
		self.table = table_
		self.table_items = ['Device1', 'Device2', 'Device3']
		self.list_source = ui.ListDataSource(self.table_items)
		self.table.data_source = self.list_source
		self.table.delegate.action = self.select_device
		
		self.dt_table = dt_table_
		self.dt_table_items = ['US/Eastern', 'US/Central', 'US/Mountain', 'US/Pacific', 'US/Alaska', 'US/Hawaii']
		self.dt_source = ui.ListDataSource(self.dt_table_items)
		self.dt_table.data_source = self.dt_source
		self.dt_table.delegate.action = self.select_time
		
		self.cwd_ = cwd_
		
		self.selector = ui.Button(title = 'Choose a device to pair', action = self.save_device)
		self.selector.y = self.table.y - 30
		self.selector.x = self.table.x - 10
		self.selector.alignment = ui.ALIGN_LEFT
		self.selector.tint_color = 'white'
		self.subview.add_subview(self.selector)
		
		self.time_selector = ui.Button(title = 'Choose a timezone ', action = self.save_time)
		self.time_selector.y = self.dt_table.y - 30
		self.time_selector.x = self.dt_table.x - 10
		self.time_selector.tint_color = 'white'
		self.time_selector.alignment = ui.ALIGN_LEFT
		self.subview.add_subview(self.time_selector)
		
		
		self.current_device = ui.Label(text = self.fetch_value('dev'), font =('Arial-ItalicMT', 12))
		self.current_device.x = self.table.x + 10
		self.current_device.y = self.table.x + self.table.height -10
		self.current_device.width = self.table.width + 150
		self.subview.add_subview(self.current_device)
		self.current_tz = ui.Label(text = self.fetch_value('tz'), font = ('Arial-ItalicMT', 12))
		self.current_tz.x = self.dt_table.x + 10
		self.current_tz.y = self.dt_table.y + self.dt_table.height-55
		self.current_tz.width = self.dt_table.width + 150
		self.subview.add_subview(self.current_tz)
		
	def select_device(self, sender):
		self.selection = self.list_source.items[sender.selected_row]
		print(self.selection)
		self.selector.title = 'Save Device' 
		self.selector.bg_color = 'orange'
		self.current_device.text = 'Change default device to ' + str(self.selection) + ' ?'
	def save_device(self,sender):
		try:
			self.device_log = {'device': self.selection}
			with open(self.cwd_ + '/log/device_settings.json', 'w') as outfile:
				json.dump(self.device_log, outfile)
			self.selector.title = 'Saved'
			self.selector.bg_color = 'None'
		except AttributeError:
			pass
	def select_time(self, sender):
		self.time_selection = self.dt_source.items[sender.selected_row]
		print(self.time_selection)
		self.time_selector.title = 'Save Timezone' 
		self.time_selector.bg_color = 'orange'
		self.current_tz.text = 'Change default to ' + str(self.time_selection) + ' ?'
	def save_time(self, sender):
		try:
			self.time_log = {'timezone': self.time_selection}
			with open(self.cwd_ + '/log/timezone_settings.json', 'w') as outfile:
				json.dump(self.time_log, outfile)
			self.time_selector.title = 'Saved'
			self.time_selector.bg_color = 'None'
		except AttributeError:
			pass
		
	def fetch_value(self,logtype):
		if logtype == 'dev':
			logname = 'device_settings.json'
			logkey = 'device'
			noneOnFile = 'No device on file'
		elif logtype == 'tz':
			logname = 'timezone_settings.json'
			logkey = 'timezone'
			noneOnFile = 'Set to US/Pacific'
		try:
			with open(self.cwd_ + '/log/' + logname) as f:
				logsource = json.load(f)
			logvalue = 'Set to ' + logsource[logkey]
		except FileNotFoundError:
			logvalue = noneOnFile
		return logvalue
