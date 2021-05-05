# Python imports
import os
import numpy as np
import datetime as datetime
import time
from pytz import timezone

# Pythonista imports
import ui


class ResultsTable(object):
	def __init__(self, subview_, table_, ac_res, etime_res):
		self.subview = subview_
		self.table = table_
		self.etime = etime_res
		self.ac = ac_res       
		self.sorted_etime = sorted(list(self.etime))
		dt_list = []     
		orig_dt_list = []   
		for i in self.etime:
			orig_dt_list.append(i.strftime("%b %d, %Y, %I:%M %p"))
		for i in self.sorted_etime:
			dt_list.append(i.strftime("%b %d, %Y, %I:%M %p"))		
		results = []
		for i in dt_list:
			results.append(i + '    ' + str(round(self.ac[np.where(np.array(orig_dt_list) == i)[0][0]],1)) + ' ppm')

		self.table_items = results        
		self.list_source = ui.ListDataSource(reversed(self.table_items))
		self.table.data_source = self.list_source
	def update_table(self, new_ac_res, new_etime_res):
		self.table.reload()
		new_sorted_etime = sorted(list(new_etime_res))
		dt_list = []
		orig_dt_list = [] 
		for i in new_sorted_etime:
			dt_list.append(i.strftime("%b %d, %Y, %I:%M %p"))		
		for i in new_etime_res:
			orig_dt_list.append(i.strftime("%b %d, %Y, %I:%M %p"))
		results = []
		for i in dt_list:
			results.append(i + '    ' + str(round(new_ac_res[np.where(np.array(orig_dt_list) == i)[0][0]],1)) + ' ppm')
		self.table.data_source =  ui.ListDataSource(reversed(results))
