import os
import json
import threading
from time import sleep
from http.server import SimpleHTTPRequestHandler

class StargateWebServer(SimpleHTTPRequestHandler):
 
    def translate_path(self, path):
        fullpath = "/home/sg1/sg1/web" + path
        return fullpath

#   def translate_path(self, path):
#         path = SimpleHTTPRequestHandler.translate_path(self, path)
#         relpath = os.path.relpath(path, os.getcwd())
#         fullpath = os.path.join('web', relpath)
#         return fullpath

    def translate_path(self, path):
        path = SimpleHTTPRequestHandler.translate_path(self, path)
        relpath = os.path.relpath(path, os.getcwd())
        fullpath = os.path.join('web', relpath)
        return fullpath
    
    # Overload log_message to suppress logs from printing to console
    def log_message(self, format, *args):
        pass
        
    def do_GET(self):
        fullPath = self.translate_path(self.path)
        if fullPath:
            try:
                with open(fullPath, 'rb') as file: 
                    self.wfile.write(file.read()) # Read the file and send the contents     
            except:
                pass
        
    def do_POST(self):
        #print('POST PATH: {}'.format(self.path))
        if self.path == '/shutdown':
            self.stargate.wormhole = False
            sleep(5)
            self.send_response(200, 'OK')
            os.system('systemctl poweroff')
            return

        if self.path == '/reboot':
            self.stargate.wormhole = False
            sleep(5)
            self.send_response(200, 'OK')
            os.system('systemctl reboot')
            return

        content_len = int(self.headers.get('content-length', 0))
        body = self.rfile.read(content_len)
        data = json.loads(body)
        #print('POST DATA: {}'.format(data))

        if self.path == '/update':
            if data['action'] == "chevron_cycle":
                self.stargate.chevrons.get(int(data['chevron_number'])).cycle_outgoing()
        
            elif data['action'] == "all_leds_off":
                self.stargate.chevrons.all_off()
                self.stargate.wormhole = False
                
            elif data['action'] == "chevron_led_on":
                self.stargate.chevrons.all_lights_on()
            
            elif data['action'] == "wormhole_on":
                self.stargate.wormhole = True
                  
            elif data['action'] == "wormhole_off":
                self.stargate.wormhole = False
            
            elif data['action'] == "symbol_forward":
                self.stargate.ring.move( 33, self.stargate.ring.forwardDirection ) # Steps, Direction
                self.stargate.ring.release()
            
            elif data['action'] == "symbol_backward":
                self.stargate.ring.move( 33, self.stargate.ring.backwardDirection ) # Steps, Direction
                self.stargate.ring.release()
                
            elif data['action'] == "volume_down":
                self.stargate.audio.volume_down()
                
            elif data['action'] == "volume_up":
                self.stargate.audio.volume_up()
                
                
        self.send_response(200, 'OK')
        self.end_headers()