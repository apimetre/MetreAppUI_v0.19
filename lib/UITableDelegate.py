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

		dt_list = []
		results = []
		for i in self.etime:
			dt_list.append(i.strftime("%b %d, %Y, %I:%M %p"))		
		for i in self.ac:
			results.append(dt_list[np.where(self.ac == i)[0][0]] + '      ' + str(round(i, 1)) + ' ppm')
		self.table_items = results        
		self.list_source = ui.ListDataSource(reversed(self.table_items))
		self.table.data_source = self.list_source
	def update_table(self, new_ac_res, new_etime_res):
		self.table.reload()
		dt_list = []
		results = []
		for i in new_etime_res:
			dt_list.append(i.strftime("%b %d, %Y, %I:%M %p"))		
		for i in new_ac_res:
			results.append(dt_list[np.where(new_ac_res == i)[0][0]] + '      ' + str(round(i, 1)) + ' ppm')
		self.table.data_source =  ui.ListDataSource(reversed(results))
	
