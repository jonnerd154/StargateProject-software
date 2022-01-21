import os
import json
from time import sleep
import urllib.parse
import collections
import platform
from http.server import SimpleHTTPRequestHandler



class StargateWebServer(SimpleHTTPRequestHandler):

    #Overload SimpleHTTPRequestHandler.log_message() to suppress logs from printing to console
    def log_message(self, format, *args): # pylint: disable=redefined-builtin
        if self.debug:
            self.stargate.log.log(self.client_address[0] + ' %s' % args[0])

    def parse_get_vars(self):
        query_string = {}
        path = self.path
        if '?' in path:
            path, tmp = path.split('?', 1)
            query_string = urllib.parse.parse_qs(tmp)
        return path, query_string

    def do_GET(self): # pylint: disable=invalid-name
        try:
            request_path, get_vars = self.parse_get_vars()

            if request_path == "/is_alive":
                data = { 'is_alive': True }

            elif request_path == "/get_address_book":
                type = get_vars.get('type')[0]
                if type == "standard":
                    data = self.stargate.addr_manager.get_book().get_standard_gates()
                elif type == "fan":
                    data = self.stargate.addr_manager.get_book().get_fan_gates()
                else:
                    all_addr = self.stargate.addr_manager.get_book().get_all_nonlocal_addresses()
                    data = collections.OrderedDict(sorted(all_addr.items()))

            elif request_path == "/get_local_address":
                data = self.stargate.addr_manager.get_book().get_local_address()

            elif request_path == "/get_dialing_status":
                data = {
                    "gate_name":                self.stargate.addr_manager.get_book().get_local_gate_name(),
                    "local_address":            self.stargate.addr_manager.get_book().get_local_address(),
                    "address_buffer_outgoing":  self.stargate.address_buffer_outgoing,
                    "locked_chevrons_outgoing": self.stargate.locked_chevrons_outgoing,
                    "address_buffer_incoming":  self.stargate.address_buffer_incoming,
                    "locked_chevrons_incoming": self.stargate.locked_chevrons_incoming,
                    "wormhole_active":          self.stargate.wormhole,
                    "black_hole_connected":     self.stargate.black_hole,
                    "connected_planet":         self.stargate.connected_planet_name,
                    "wormhole_open_time":       self.stargate.wh_manager.open_time,
                    "wormhole_max_time":        self.stargate.wh_manager.wormhole_max_time,
                    "wormhole_time_till_close": self.stargate.wh_manager.get_time_remaining()
                }

            elif request_path == "/get_system_info":
                data = {
                    "gate_name":                      self.stargate.addr_manager.get_book().get_local_gate_name(),
                    "local_stargate_address":         self.stargate.addr_manager.get_book().get_local_address(),
                    "local_stargate_address_string":  self.stargate.addr_manager.get_book().get_local_address_string(),
                    "subspace_public_key":            self.stargate.subspace_client.get_public_key(),
                    "subspace_ip_address_config":     self.stargate.subspace_client.get_configured_ip(),
                    "subspace_ip_address_active":     self.stargate.subspace_client.get_subspace_ip(True),
                    "lan_ip_address":                 self.stargate.subspace_client.get_ip_from_interface( 'wlan0' ),
                    "software_version":               str(self.stargate.sw_updater.get_current_version()),
                    "software_update_last_check":     self.stargate.cfg.get('software_update_last_check'),
                    "software_update_status":         self.stargate.cfg.get('software_update_status'),
                    "python_version":                 platform.python_version(),
                    "internet_available":             self.stargate.net_tools.has_internet_access(),
                    "subspace_available":             self.stargate.subspace_client.is_online(),
                    "standard_gate_count":            len(self.stargate.addr_manager.get_book().get_standard_gates()),
                    "fan_gate_count":                 len(self.stargate.addr_manager.get_book().get_fan_gates()),
                    "last_fan_gate_update":           self.stargate.cfg.get('last_fan_gate_update'),
                    "dialer_mode":                    self.stargate.dialer.type,
                    "hardware_mode":                  self.stargate.electronics.name
                }

            elif request_path == "get_symbols":
                data = {
                    "symbols": self.stargate.symbol_manager.get_all_ddslick()
                }

            else:
                # Unhandled GET request: send a 404
                self.send_response(404)
                self.end_headers()
                return

            content = json.dumps( data )
            self.send_response(200)
            self.send_header("Content-type", "text/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Headers", 'Authorization, Content-Type')
            self.send_header("Access-Control-Allow-Methods", 'GET')
            self.end_headers()
            self.wfile.write(content.encode())

        except: # pylint: disable=bare-except
            if self.debug:
                raise

            # Encountered an exception: send a 500
            self.send_response(500)
            self.end_headers()

    def do_POST(self): # pylint: disable=invalid-name
        try:
            #print('POST PATH: {}'.format(self.path))

            content_len = int(self.headers.get('content-length', 0))
            body = self.rfile.read(content_len)
            data = json.loads(body)
            #print('POST DATA: {}'.format(data))

            if self.path == '/do':

                ##### DO ACTION HANDLERS BELOW ####
                if data['action'] == '/shutdown':
                    self.stargate.wormhole = False
                    sleep(5)
                    self.send_response(200, 'OK')
                    os.system('systemctl poweroff')
                    return

                elif data['action'] == '/reboot':
                    self.stargate.wormhole = False
                    sleep(5)
                    self.send_response(200, 'OK')
                    os.system('systemctl reboot')
                    return

                elif data['action'] == "chevron_cycle":
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
                    self.stargate.ring.move( 33, self.stargate.ring.forward_direction ) # Steps, Direction
                    self.stargate.ring.release()

                elif data['action'] == "symbol_backward":
                    self.stargate.ring.move( 33, self.stargate.ring.backward_direction ) # Steps, Direction
                    self.stargate.ring.release()

                elif data['action'] == "volume_down":
                    self.stargate.audio.volume_down()

                elif data['action'] == "volume_up":
                    self.stargate.audio.volume_up()

                elif data['action'] == "sim_incoming":
                    if not self.stargate.wormhole: # If we don't already have an established wormhole
                        # Get the loopback address and dial it
                        for symbol_number in self.stargate.addr_manager.get_book().get_local_loopback_address():
                            self.stargate.address_buffer_incoming.append(symbol_number)

                        self.stargate.address_buffer_incoming.append(7) # Point of origin
                        self.stargate.centre_button_incoming = True

                elif data['action'] == "subspace_up":
                    print("Subspace UP")

                elif data['action'] == "subspace_down":
                    print("Subspace DOWN")
            elif self.path == '/update':

                ##### UPDATE DATA HANDLERS BELOW ####

                if data['action'] == "set_local_stargate_address":
                    continue_to_save = True
                    # Parse the address
                    try:
                        address = [ data['S1'], data['S2'], data['S3'], data['S4'], data['S5'], data['S6'] ]
                    except KeyError:
                        data = { "success": False, "error": "Required fields missing or invalid request" }
                        continue_to_save = False

                    # Validate that this is an acceptable address
                    if continue_to_save:
                        verify_avail, error, entry = self.stargate.addr_manager.verify_address_available(address) # pylint: disable=unused-variable
                        if verify_avail == "VERIFY_OWNED":
                            # This address is in use by a fan gate, but someone might be (re)configuring their own gate.
                            try:
                                if data['owner_confirmed']:
                                    pass # Valid, continue to save
                                else:
                                    data = { "success": False, "error": error }
                                    continue_to_save = False
                            except KeyError:
                                data = { "success": False, "extend": "owner_unconfirmed", "error": "This address is in use by a Fan Gate - \"{entry['name']}\"" }
                                continue_to_save = False
                        elif verify_avail is False:
                            # This address is in use by a standard gate
                            data = { "success": False, "error": error }
                            continue_to_save = False
                        else:
                            pass # Address not in use, clear to proceed

                    # Store the address:
                    if continue_to_save:
                        self.stargate.addr_manager.get_book().set_local_address(address)
                        data = { "success": True, "message": "There are no conflicts with your chosen address.<br><br>Local Address Saved." }

                    self.send_json_response(data)
                    return

                elif data['action'] == "set_subspace_ip":
                    # TODO: Validate the IP address again (client did it, but we should too)
                    success = self.stargate.subspace_client.set_ip_address(data['ip'])

                    if success:
                        data = { "success": success, "message": "Subspace IP Address Saved." }
                    else:
                        data = { "success": success, "message": "There was an error while saving the IP Address." }

                    self.send_json_response(data)
                    return



            elif self.path == '/dhd_press':
                symbol_number = int(data['symbol'])

                if symbol_number > 0:
                    self.stargate.keyboard.queue_symbol(symbol_number)
                elif symbol_number == 0:
                    self.stargate.keyboard.queue_center_button()

            elif self.path == '/incoming_press':
                symbol_number = int(data['symbol'])

                if symbol_number > 0:
                    self.stargate.address_buffer_incoming.append(symbol_number)
                elif symbol_number == 0:
                    self.stargate.centre_button_incoming = True


            self.send_response(200, 'OK')
            self.end_headers()

        except: # pylint: disable=bare-except
            if self.debug:
                raise

            # Encountered an exception: send a 500
            self.send_response(500)
            self.end_headers()

    def send_json_response(self, data):
        content = json.dumps( data )
        self.send_response(200)
        self.send_header("Content-type", "text/json")
        self.end_headers()
        self.wfile.write(content.encode())
