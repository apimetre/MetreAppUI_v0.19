
import os
import shutil
import console

def main():
	try:
		cloud_dir = '/private/var/mobile/Library/Mobile Documents/iCloud~com~omz-software~Pythonista3/Documents'
    	
		root_dir = os.path.abspath(os.path.expanduser('~/Documents/' + 'MetreiOS'))
		sortedList = sorted([x for x in os.listdir(root_dir) if x.startswith('MetreAppUI')])

		most_recent_version = sortedList[-1]
		shutil.copy(cloud_dir + '/' + 'log_003.json', root_dir + '/' + most_recent_version  + '/log/' + 'log_003.json')
		console.alert('Log data successfully recovered', 'Continue')
	except FileNotFoundError:
		console.alert('Log transfer failed. Be sure the MetreiOS app is installed. Contact support for help')
    
if __name__ ==  '__main__':
    main()
