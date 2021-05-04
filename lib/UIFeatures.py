# Pythonista imports
import ui
import objc_util
class ProgressBar():
    def __init__(self, fillbar_, fillbar_outline_, fullbar_):
        self.fillbar_ = fillbar_
        self.fillbar_outline_ = fillbar_outline_
        self.fullbar_ = fullbar_
    def update_progress_bar(self, percent_width):
        '''redraw the progress bar and update status text'''
        if percent_width < 0.99:
            self.fillbar_.width = self.fullbar_ * percent_width
        else:
            self.fillbar_.width = self.fullbar_ * 0.99
                
class ConsoleAlert():
    def __init__(self, message_, view_):
        self.message = message_
        self.view = view_
        self.field = ui.Label(name = 'field', text = self.message, number_of_lines = 0, alignment = ui.ALIGN_CENTER, font = ("<system-bold>", 12), scales_font = True, border_width = 2, border_color = 'red', background_color = 'white'
       )
        self.field.y = self.view.height * 0.52
        self.field.x = self.view.width * 0.25
        self.field.width = self.view.width * 0.5
        self.field.height = self.view.height * 0.17
        self.button = ui.Button(title='X', action=self.tap_to_close)
        self.button.y = self.field.y
        self.button.x = self.field.x
        self.view.add_subview(self.field)
        self.view.add_subview(self.button)
        #print(self.message)
        ui.delay(self.close_window, 3) 
        
        
        
    def tap_to_close(self, sender):
        self.field.alpha = 0
        self.button.alpha = 0
    def close_window(self):
        self.field.alpha = 0
        self.button.alpha = 0
    
