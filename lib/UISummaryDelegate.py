# Python imports
import os
import numpy as np
from io import BytesIO
import datetime as datetime
import time
from pytz import timezone
import json
import matplotlib.pyplot as plt
from matplotlib.dates import num2date, date2num, num2epoch

# Pythonista imports
import ui
import Image

class SummaryDelegate(object):
	def __init__(self, subview_, dailyview_, weeklyview_, cwd_):
		self.subview = subview_
		self.dailyview = dailyview_
		self.weeklyview = weeklyview_
		self.cwd_ = cwd_
		with open(self.cwd_+ '/log/timezone_settings.json') as f:
			tzsource = json.load(f)
			self.tz = tzsource["timezone"]
		self.get_log()
		try:
			self.weeklyview.image = self.plotWeekly()
		except:
			self.weeklyview.image = self.blankPlot()
		try:
			self.dailyview.image = self.plotDaily()
		except:
			self.dailyview.image = self.blankPlot()
	def get_log(self):
		with open(self.cwd_ + '/log/log_003.json') as json_file:
			self.log = json.load(json_file)
		self.etime = []
		self.weektime = []
		self.dtDateTime = []
		for val in self.log['Etime']:
			tval = datetime.datetime.fromtimestamp(int(val)).astimezone(timezone(self.tz))
			year, weeknum = tval.strftime("%Y-%U").split('-')
			plottval = datetime.datetime.fromtimestamp(int(val)).astimezone(timezone(self.tz))
			weekcalc = str(year) + '-W' + str(weeknum)
			day_of_week = datetime.datetime.strptime(weekcalc + '-1', "%Y-W%W-%w")
			self.weektime.append(day_of_week)
			self.etime.append(tval)
			self.dtDateTime.append(plottval)
		self.acetone = np.array(self.log['Acetone'])
		self.vectorized = []
		for i in range(0, len(self.acetone)):
			self.vectorized.append([self.weektime[i], self.acetone[i], self.dtDateTime[i]])
		self.varray = np.array(self.vectorized)
			

	def plotWeekly(self):
		self.weekly_means = {}
		for i in np.unique(self.varray[:,0]):
			unw = self.varray[np.where(self.varray[:,0]==i)]
			self.weekly_means[i] = np.mean(unw[:,1])
			
		self.wdates = []
		self.waces = []
		self.wdatelabels = []
		for key, value in self.weekly_means.items():
			self.wdates.append(key)
			self.waces.append(value)
			self.wdatelabels.append(key.strftime("%b %d, %Y"))
		plt.figure()
		staticBar = plt.axes()
		staticBar.bar(self.wdates, self.waces, width=3, color='grey')
		staticBar.set_xticks(self.wdates)
		staticBar.set_xticklabels(self.wdatelabels, rotation=45, fontsize=24)
		staticBar.set_ylabel('Average Values (ppm)', fontsize=24, fontweight='bold')
		staticBar.set_xlabel('Week', fontsize=24, fontweight='bold')
		staticBar.xaxis_date()
		plt.yticks(fontsize=24)
		plt.tight_layout()
		sB = BytesIO()
		plt.savefig(sB, format='png', dpi=600)
		self.weekly_img = ui.Image.from_data(sB.getvalue())
		return self.weekly_img

	def plotDaily(self):
		weekly_values = {}
		for i in np.unique(self.varray[:,0]):
			wkv = self.varray[np.where(varray[:,0] == i)]
			weekly_values[i] = wkv
		
		fotw = datetime.datetime.strptime(datetime.datetime.now().strftime("%Y-W%U")  + '-1', '%Y-W%W-%w')
		fotw_string = fotw.strftime('%b %d %Y')
		weekrange = [fotw]
		weekrange_string = [fotw_string]
		for i in range (1,7):
			weekrange.append((fotw + datetime.timedelta(days=i)))
			weekrange_string.append((fotw + datetime.timedelta(days=i)).strftime('%b %d %Y'))
		try:
			fotwData = weekly_values[fotw]
			day = [x.strftime('%Y-%m-%d') for x in fotwData[:,-1]]
			fotwData[:,-1] = day
			daily_means = {}
			for i in np.unique(fotwData[:,-1]):
				fotwd = fotwData[np.where(fotwData[:,-1] == i)]
				daily_means[i] = np.mean(fotwd[:,1])
			ddates = []
			daces = []

			for key, value in daily_means.items():
				ddates.append(datetime.datetime.strptime(key, '%Y-%m-%d'))
				daces.append(value)

		except (ValueError, KeyError) as e:
			ddates = [datetime.datetime.now()]
			daces = [0]

		plt.figure()
		dax = plt.axes()
		dax.bar(ddates, daces, width = 0.5, color = 'red')
		dax.set_xticks(weekrange)
		weekrange_daystring = ['Mon', 'Tues', 'Wed', 'Thurs', 'Fri', 'Sat', 'Sun']
		dax.set_xticklabels(weekrange_daystring, rotation = 45, fontsize = 24, fontweight = 'bold')
		dax.xaxis_date()
		dax.set_ylabel('Average Values (ppm)', fontweight = 'bold', fontsize = 24)
		dax.set_ylim(0,30)
		plt.yticks(fontsize=24)
		plt.tight_layout()
		dB = BytesIO()
		plt.savefig(dB, format = 'png', dpi = 600)
		daily_img = ui.Image.from_data(dB.getvalue())
		return daily_img
		
	def blankPlot(self):
		blankfig = plt.figure()
		bax = blankfig.add_subplot(111)
		bax.text(2, 6, r'Your test results will show up here once processed', fontsize=15)
		bB = BytesIO()
		plt.savefig(bB, format = 'png', dpi = 600)
		blank_img = ui.Image.from_data(bB.getvalue())
		return blank_img
