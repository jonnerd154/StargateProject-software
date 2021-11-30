import os
import json
import threading
from time import sleep
import urllib.parse
import collections
from http.server import SimpleHTTPRequestHandler

class StargateWebServer(SimpleHTTPRequestHandler):
    
    #Overload SimpleHTTPRequestHandler.log_message() to suppress logs from printing to console
    def log_message(self, format, *args):
        pass
       
    def parse_GET_vars(self):
        qs = {}
        path = self.path
        if '?' in path:
            path, tmp = path.split('?', 1)
            qs = urllib.parse.parse_qs(tmp)
        return path, qs
     
    def do_GET(self):
        try:
            request_path, get_vars = self.parse_GET_vars()
            
            if request_path == '/get':
                entity = get_vars.get('entity')[0]

                if ( entity == "standard_gates"):
                    content = json.dumps( self.stargate.addrManager.getBook().get_standard_gates() )
            
                elif( entity == "fan_gates" ):
                    content = json.dumps( self.stargate.addrManager.getBook().get_fan_gates() )
                
                elif( entity == "all_gates" ):
                    all_addr = self.stargate.addrManager.getBook().get_all_nonlocal_addresses()
                    ordered_dict = collections.OrderedDict(sorted(all_addr.items()))
                    content = json.dumps( ordered_dict )
            
                elif( entity == "local_address" ):
                    content = json.dumps( self.stargate.addrManager.getBook().get_local_address() )
                
                self.send_response(200)
                self.send_header("Content-type", "text/json")
                self.end_headers()
                self.wfile.write(content.encode())
               
            else:
                # Unhandled request: send a 404
                self.send_response(404)
                self.end_headers()
        
            return
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
                
        elif self.path == '/dhd_press':
            symbol_number = int(data['symbol'])
            
            if symbol_number > 0:
                self.stargate.keyboard.queue_symbol(symbol_number)
            elif symbol_number == 0:
                self.stargate.fan_gate_online_status = False #TODO: This isn't necessarily true.
                self.stargate.keyboard.queue_center_button()
        
                
        self.send_response(200, 'OK')
        self.end_headers()