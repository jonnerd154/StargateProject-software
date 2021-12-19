import os
import json
import threading
from time import sleep
import urllib.parse
import collections
from http.server import SimpleHTTPRequestHandler

class StargateWebServer(SimpleHTTPRequestHandler):

    #Overload SimpleHTTPRequestHandler.log_message() to suppress logs from printing to console
    # *** Comment this out for debugging!! ***
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

                elif( entity == "status" ):
                	data = {
                		"address_buffer_outgoing":  self.stargate.address_buffer_outgoing,
                		"locked_chevrons_outgoing": self.stargate.locked_chevrons_outgoing,
                		"address_buffer_incoming":  self.stargate.address_buffer_incoming,
                		"locked_chevrons_incoming": self.stargate.locked_chevrons_incoming,
                		"wormhole_active":          self.stargate.wormhole,
                		"black_hole_connected":     self.stargate.black_hole,
                		"connected_planet":         self.stargate.connected_planet_name,
                		"wormhole_open_time":       self.stargate.wh.open_time,
                		"wormhole_max_time":        self.stargate.wh.wormhole_max_time,
                		"wormhole_time_till_close": self.stargate.wh.get_time_remaining()
                	}
                	content = json.dumps( data )

                elif( entity == "info" ):
                	data = {
                		"local_stargate_address":         self.stargate.addrManager.getBook().get_local_address(),
                		"local_stargate_address_string":  self.stargate.addrManager.getBook().get_local_address_string(),
                		"subspace_public_key":            self.stargate.subspace.get_public_key(),
                		"subspace_ip_address":            self.stargate.subspace.get_subspace_ip(),
                		"lan_ip_address":                 self.stargate.subspace.get_lan_ip(),
                		"software_version":               self.stargate.swUpdater.get_current_version(),
                        "internet_available":			  self.stargate.netTools.has_internet_access(),
                        "subspace_available":			  self.stargate.subspace.is_online(),
                        "standard_gate_count":	  		  len(self.stargate.addrManager.getBook().get_standard_gates()),
                        "fan_gate_count":	  		      len(self.stargate.addrManager.getBook().get_fan_gates())
                	}
                	content = json.dumps( data )

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

            # raise # *** Un-comment for debugging!! ***

            # Encountered an exception: send a 500
            self.send_response(500)
            self.end_headers()

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

            elif data['action'] == "sim_incoming":
                if ( not self.stargate.wormhole ): # If we don't already have an established wormhole
                    # Get the loopback address and dial it
                    for symbol_number in self.stargate.addrManager.addressBook.get_local_loopback_address():
                        self.stargate.address_buffer_incoming.append(symbol_number)

                    self.stargate.address_buffer_incoming.append(7) # Point of origin
                    self.stargate.centre_button_incoming = True


        elif self.path == '/dhd_press':
            symbol_number = int(data['symbol'])

            if symbol_number > 0:
                self.stargate.keyboard.queue_symbol(symbol_number)
            elif symbol_number == 0:
                self.stargate.fan_gate_online_status = False #TODO: This isn't necessarily true.
                self.stargate.keyboard.queue_center_button()

        elif self.path == '/incoming_press':
            symbol_number = int(data['symbol'])

            if symbol_number > 0:
                self.stargate.address_buffer_incoming.append(symbol_number)
            elif symbol_number == 0:
                self.stargate.centre_button_incoming = True


        self.send_response(200, 'OK')
        self.end_headers()
