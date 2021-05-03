import ui

POPOVER_WIDTH = 500
SEND_TEXT_VIEW_HEIGHT = 30
POPOVER_DIALOG_NAME = 'send_ui_test.py'

class SendTextFieldView(ui.View):
    def __init__(self, text, button_name_text, button_fn, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.field_text = text
        self.button_name = button_name_text
        self.button_pressed_fn = button_fn
        self.text_field_view = None
        self.button_view = None
        self.TEXTFIELD_FRAME = (0,0,int(self.frame[2] * 0.85),self.frame[3])
        AUTO = 0 # changing these params does not seem to matter...they seem driven by the button_view
        self.BUTTON_FRAME = (int(self.frame[2] * 0.85 + 3), 0, AUTO, AUTO)
        self.make_views()
        
    def make_views(self):
        # create the ui.Image
        self.text_field_view = ui.TextField(
                                    frame=self.TEXTFIELD_FRAME,
                                    background_color='white',
                                    border_width=1,
                                    border_color='#d8d8d8',
                                    text=self.field_text,
                                    font=('Courier', 10),
                                    )
        self.text_field_view.delegate = self
        # create the ui.Button
        self.button_view = ui.Button(
                                    flex='WL',
                                    title=self.button_name,
                                    frame=self.BUTTON_FRAME,
                                    action=self.button_pressed,
                                    border_color='#6b6b6b',
                                    border_width=1,
                                    corner_radius=5,
                                    )
        t = self.text_field_view.frame
        b = self.button_view.frame

        text_field_end = self.frame[2] - b[2] - 6
        self.text_field_view.frame = (t[0],t[1],text_field_end,t[3])
        self.button_view.frame = (text_field_end+3,b[1],b[2],b[3])
        # add objects to the view
        self.add_subview(self.text_field_view)
        self.add_subview(self.button_view)
        
    def button_pressed(self, sender):
        self.button_pressed_fn(self.text_field_view.text)

    def textfield_did_change(self,tv):
        if tv.text:
            # next lines deal with iPad keyboard artifact where all keys except for quotes are single byte ascii codes.
            self.text_field_view.text = tv.text.replace(chr(8216), "'") # replace single close quote with single byte ascii code for single quote
            self.text_field_view.text = tv.text.replace(chr(8217), "'") # close quote follows open quote, so have to filter this too
            self.text_field_view.text = tv.text.replace(chr(96), "'") # close quote follows open quote, so have to filter this too
            self.text_field_view.text = tv.text.replace(chr(8220), '"') # replace double close quote with single byte ascii code for double quote
            self.text_field_view.text = tv.text.replace(chr(8221), '"') # close double quote follows open double quote, so have to filter this too

class ViewListView(ui.View):
    def __init__(self, texts, send_fn, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.texts = texts
        self.send_fn = send_fn
        self.VIEW_HEIGHT = SEND_TEXT_VIEW_HEIGHT
        self.make_views()
        
    def make_views(self):
        i = 0
        for text in self.texts:
            view = SendTextFieldView(text,' Send ', self.send_fn, frame=(0, i * (self.VIEW_HEIGHT + 2), self.frame[2], self.VIEW_HEIGHT))
            self.add_subview(view)
            i+=1
        self.frame = (self.frame[0], self.frame[1], self.frame[2], i * (self.VIEW_HEIGHT + 2))