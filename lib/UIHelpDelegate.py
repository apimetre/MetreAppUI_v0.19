# Python imports
import os
import shutil
import numpy as np

# Pythonista imports
import ui
import console


class HelpDelegate(object): 
    def __init__(self, hview_, online_instructions_, online_qa_, recover_button_):
        self.hview = hview_
        self.online_instructions = online_instructions_
        self.online_qa = online_qa_
        self.recover_button = recover_button_
        
    
        self.online_instructions.action = self.helpView
        self.online_qa.action = self.qaView     
        self.recover_button.action = self.recoverView

    def recover_log(self,sender):
        try:
            cloud_dir = '/private/var/mobile/Library/Mobile Documents/iCloud~com~omz-software~Pythonista3/Documents'

            root_dir = os.path.abspath(os.path.expanduser('~/Documents/' + 'MetreiOS'))
            sortedList = sorted([x for x in os.listdir(root_dir) if x.startswith('MetreAppUI')])
            
            most_recent_version = sortedList[-1]
            shutil.copy(cloud_dir + '/' + 'log_003.json', root_dir + '/' + most_recent_version  + '/log/' + 'log_003.json')
            console.alert('Log data successfully recovered', 'Continue')
        except FileNotFoundError:
            console.alert('Log transfer failed. Be sure the MetreiOS app is installed. Contact support for help')
            
                          
    def helpView(self, sender):
        instructions_url = 'https://www.metre.ai/resources/metreui/instructions'
        
        helpWindow = ui.WebView()
        helpWindow.tint_color = 'red'
        self.hview.add_subview(helpWindow)
        helpWindow.load_url(instructions_url)
        helpWindow.present()
        
    def qaView(self, sender):
        qa_url = 'https://www.metre.ai/resources/metreui/qa'
        qaWindow = ui.WebView()
        qaWindow.tint_color = 'red'
        self.hview.add_subview(qaWindow)
        qaWindow.load_url(qa_url) 
        qaWindow.present()
        
        
    def recoverView(self, sender):
        recover_dialog = ui.load_view('retrieve_log')
        self.hview.add_subview(recover_dialog)
        recover_button = recover_dialog['retrieve_data_button']
        recover_button.action = self.recover_log
        recover_dialog.present()
        

