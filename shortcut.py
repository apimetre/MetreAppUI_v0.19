import plistlib
import http.server
import webbrowser
import uuid
from io import BytesIO
from PIL import Image
import photos
import notification
import console
import os, json
import urllib.request
from objc_util import nsurl, UIApplication
import ui

class ConfigProfileHandler (http.server.BaseHTTPRequestHandler):
    config = None
    def do_GET(s):
        s.send_response(200)
        s.send_header('Content-Type', 'application/x-apple-aspen-config')
        s.end_headers()
        #config_bytes = json.dumps(ConfigProfileHandler.config).encode('utf-8')
        plist_string = plistlib.writePlistToBytes(ConfigProfileHandler.config)
        s.wfile.write(plist_string)
    def log_message(self, format, *args):
        pass

def run_server(config):
	
    ConfigProfileHandler.config = config
    #app = UIApplication.sharedApplication()
    #URL = 'http://www.metre.ai/home'
    #app.openURL(nsurl(URL))
    #webbrowser.open('safari-' + URL)
    server_address = ('', 0)
    httpd = http.server.HTTPServer(server_address, ConfigProfileHandler)
    sa = httpd.socket.getsockname()
    webbrowser.open_new_tab('safari-http://localhost:' + str(sa[1]))
    #webbrowser.get('safari').open_new_tab('http://google.com')
    httpd.handle_request()
    #webbrowser.get('safari').open_new_tab('http://metre.ai/home')
    #app = UIApplication.sharedApplication()
    #URL = 'http://www.metre.ai/home'
    #app.openURL_(nsurl(URL))
    #webbrowser.open('safari-http://metre.ai/home')

def main():
    console.alert('Shortcut Generator', "This script adds a shortcut icon to running the MetreiOS app on your homepage. Your default browser MUST be Safari", 'Continue')
    # Fetch config json
    root_dir = os.path.abspath(os.path.expanduser('~Documents/' + 'MetreiOS'))
    with open('../metre_ios_install_config.json') as f:
        configs = json.load(f)
    
    currentversion = configs['git_repo']
    label = 'MetreiOS'
    url = 'pythonista3://MetreiOS' + '/' + currentversion + '/MainMetre.py?action=run'
    
    img = Image.open(BytesIO(urllib.request.urlopen("https://drive.google.com/uc?export=view&id=1--lLdK8dHtBOBwsZyFu0g3TRIjhA_0XK").read()))
    
    console.show_activity('Preparing Configuration profile...')
    data_buffer = BytesIO()
    img.save(data_buffer, 'PNG')
    icon_data = data_buffer.getvalue()
    unique_id = uuid.uuid4().urn[9:].upper()
    config = {'PayloadContent': [{'FullScreen': True,
            'Icon': plistlib.Data(icon_data), 'IsRemovable': True,
            'Label': label, 'PayloadDescription': 'Configures Web Clip',
            'PayloadDisplayName': label,
            'PayloadIdentifier': 'com.omz-software.shortcut.' + unique_id,
            'PayloadOrganization': 'omz:software',
            'PayloadType': 'com.apple.webClip.managed',
            'PayloadUUID': unique_id, 'PayloadVersion': 1,
            'Precomposed': True, 'URL': url}],
            'PayloadDescription': label,
            'PayloadDisplayName': label + ' (Shortcut)',
            'PayloadIdentifier': 'com.omz-software.shortcut.' + unique_id,
            'PayloadOrganization': 'omz:software',
            'PayloadRemovalDisallowed': False, 'PayloadType':
            'Configuration', 'PayloadUUID': unique_id, 'PayloadVersion': 1}
    console.hide_activity()
    run_server(config)
    

if __name__ ==  '__main__':
    main()
