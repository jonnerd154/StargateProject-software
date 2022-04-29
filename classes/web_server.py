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
        if self.stargate.cfg.get("control_api_debug_enable"):
            self.stargate.log.log(f'{self.client_address[0]} {str(args[0])}')

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

            if request_path == "/get/is_alive":
                data = { 'is_alive': True }

            elif request_path == "/get/address_book":
                data = {}
                record_type = get_vars.get('type')[0]
                if record_type == "standard":
                    data['address_book'] = self.stargate.addr_manager.get_book().get_standard_gates()
                elif record_type == "fan":
                    data['address_book'] = self.stargate.addr_manager.get_book().get_fan_and_lan_addresses()
                else:
                    all_addr = self.stargate.addr_manager.get_book().get_all_nonlocal_addresses()
                    data['address_book'] = collections.OrderedDict(sorted(all_addr.items()))

                data['summary'] = self.stargate.addr_manager.get_summary_from_book(data['address_book'], True)
                data['galaxy_path'] = self.stargate.galaxy_path

            elif request_path == "/get/local_address":
                data = self.stargate.addr_manager.get_book().get_local_address()

            elif request_path == "/get/dialing_status":
                data = {
                    "gate_name":                self.stargate.addr_manager.get_book().get_local_gate_name(),
                    "local_address":            self.stargate.addr_manager.get_book().get_local_address(),
                    "address_buffer_outgoing":  self.stargate.address_buffer_outgoing,
                    "locked_chevrons_outgoing": self.stargate.locked_chevrons_outgoing,
                    "address_buffer_incoming":  self.stargate.address_buffer_incoming,
                    "locked_chevrons_incoming": self.stargate.locked_chevrons_incoming,
                    "wormhole_active":          self.stargate.wormhole_active,
                    "black_hole_connected":     self.stargate.black_hole,
                    "connected_planet":         self.stargate.connected_planet_name,
                    "wormhole_open_time":       self.stargate.wh_manager.open_time,
                    "wormhole_max_time":        self.stargate.wh_manager.wormhole_max_time,
                    "wormhole_time_till_close": self.stargate.wh_manager.get_time_remaining(),
                    "ring_position":            self.stargate.ring.get_position(),
                    "speed_dial_full_address":  self.stargate.cfg.get('dialing_address_book_dials_full_address')
                }

            elif request_path == "/get/system_info":
                data = {
                    "gate_name":                      self.stargate.addr_manager.get_book().get_local_gate_name(),
                    "local_stargate_address":         self.stargate.addr_manager.get_book().get_local_address(),
                    "local_stargate_address_string":  self.stargate.addr_manager.get_book().get_local_address_string(),
                    "subspace_public_key":            self.stargate.subspace_client.get_public_key(),
                    "subspace_ip_address_config":     self.stargate.subspace_client.get_configured_ip(),
                    "subspace_ip_address_active":     self.stargate.net_tools.get_subspace_ip(True),
                    "lan_ip_address":                 self.stargate.net_tools.get_ip_by_interface_list( [ 'wlan0', 'eth0', 'en0', 'en1' ] ),
                    "software_version":               str(self.stargate.sw_updater.get_current_version()),
                    "software_update_last_check":     self.stargate.cfg.get('software_update_last_check'),
                    "software_update_status":         self.stargate.cfg.get('software_update_status'),
                    "python_version":                 platform.python_version(),
                    "internet_available":             self.stargate.net_tools.has_internet_access(),
                    "subspace_available":             self.stargate.subspace_client.is_online(),
                    "standard_gate_count":            len(self.stargate.addr_manager.get_book().get_standard_gates()),
                    "fan_gate_count":                 len(self.stargate.addr_manager.get_book().get_fan_gates()),
                    "lan_gate_count":                 len(self.stargate.addr_manager.get_book().get_lan_gates()),
                    "fan_gate_last_update":           self.stargate.cfg.get('fan_gate_last_update'),
                    "dialer_mode":                    self.stargate.dialer.type,
                    "hardware_mode":                  self.stargate.electronics.name,
                    "audio_volume":                   self.stargate.audio.volume,
                    "galaxy":                         self.stargate.galaxy
                }

                # Put the lifetime stats in here too.
                for key, value in self.stargate.dialing_log.get_summary().items():
                    data['stats_'+key] = value.get('value')

            elif request_path == "/get/hardware_status":
                data = {
                    "chevrons":                       self.stargate.chevrons.get_status(),
                    "glyph_ring":                     self.stargate.ring.get_status()
                }

            elif request_path == "/get/dhd_symbols":
                data = self.stargate.symbol_manager.get_dhd_symbols()

            elif request_path == "/get/symbols":
                data = {
                    "symbols": self.stargate.symbol_manager.get_all_ddslick()
                }

            elif request_path == "/get/symbols_all":
                data = self.stargate.symbol_manager.get_all()

            elif request_path == "/get/config":
                data = collections.OrderedDict(sorted(self.stargate.cfg.get_all_configs().items()))

            else:
                # Unhandled GET request: send a 404
                self.send_response(404, 'Not Found')
                self.end_headers()
                return

            content = json.dumps( data )
            self.send_response(200, 'OK')
            self.send_header("Content-type", "text/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Headers", 'Authorization, Content-Type')
            self.send_header("Access-Control-Allow-Methods", 'GET')
            self.end_headers()
            self.wfile.write(content.encode())

        except: # pylint: disable=bare-except
            if self.stargate.cfg.get("control_api_debug_enable"):
                raise

            # Encountered an exception: send a 500
            self.send_response(500, "Exception")
            self.end_headers()

    def do_POST(self): # pylint: disable=invalid-name
        try:
            #print('POST PATH: {}'.format(self.path))

            content_len = int(self.headers.get('content-length', 0))
            body = self.rfile.read(content_len)
            try:
                data = json.loads(body)
            except: # pylint: disable=bare-except
                data = {}

            #print('POST DATA: {}'.format(data))

            ##### DO ACTION HANDLERS BELOW ####
            if self.path == '/do/shutdown':
                self.stargate.wormhole_active = False
                sleep(5)
                self.send_response(200, 'OK')
                self.end_headers()
                os.system('systemctl poweroff')
                return

            if self.path == '/do/reboot':
                self.stargate.wormhole_active = False
                sleep(5)
                self.send_response(200, 'OK')
                self.end_headers()
                os.system('systemctl reboot')
                return

            if self.path == '/do/restart':
                if not self.stargate.app.is_daemon:
                    self.stargate.log.log("Software Reboot Requested, but not running as Daemon. Unable.")
                    self.send_response(200, 'Unable, software not running as daemon.')
                    self.end_headers()
                    return

                self.stargate.wormhole_active = False
                sleep(5)
                self.send_response(200, 'OK')
                os.system('systemctl restart stargate.service')
                return

            if self.path == "/do/chevron_cycle":
                self.stargate.chevrons.get(int(data['chevron_number'])).cycle_outgoing()
                data = { "success": True }

            elif self.path == "/do/all_chevron_leds_off":
                self.stargate.chevrons.all_off()
                self.stargate.wormhole_active = False
                data = { "success": True }

            elif self.path == "/do/all_chevron_leds_on":
                self.stargate.chevrons.all_lights_on()
                data = { "success": True }

            elif self.path == "/do/wormhole_on":
                if not self.stargate.wormhole_active:
                    self.stargate.wormhole_active = True
                    data = { "success": True }
                else:
                    data = { "success": False, "message": "A wormhole is already established." }

            elif self.path == "/do/wormhole_off":
                self.stargate.wormhole_active = False
                data = { "success": True }

            elif self.path == "/do/symbol_forward":
                self.stargate.ring.move( 33, self.stargate.ring.forward_direction ) # Steps, Direction
                self.stargate.ring.release()
                data = { "success": True }

            elif self.path == "/do/symbol_backward":
                self.stargate.ring.move( 33, self.stargate.ring.backward_direction ) # Steps, Direction
                self.stargate.ring.release()
                data = { "success": True }

            elif self.path == "/do/volume_down":
                self.stargate.audio.volume_down()
                data = { "success": True }

            elif self.path == "/do/volume_up":
                self.stargate.audio.volume_up()
                data = { "success": True }

            elif self.path == "/do/simulate_incoming":
                if not self.stargate.wormhole_active: # If we don't already have an established wormhole
                    # Get the loopback address and dial it
                    for symbol_number in self.stargate.addr_manager.get_book().get_local_loopback_address():
                        self.stargate.address_buffer_incoming.append(symbol_number)

                    self.stargate.address_buffer_incoming.append(7) # Point of origin
                    self.stargate.centre_button_incoming = True
                    data = { "success": True }
                else:
                    data = { "success": False, "message": "A wormhole is already established." }

            elif self.path == "/do/subspace_up":
                print("Subspace UP")
                data = { "success": False, "message": "API NOT IMPLEMENTED" }

            elif self.path == "/do/subspace_down":
                print("Subspace DOWN")
                data = { "success": False, "message": "API NOT IMPLEMENTED" }

            elif self.path == "/do/dhd_press":
                symbol_number = int(data['symbol'])

                if symbol_number > 0:
                    self.stargate.keyboard.queue_symbol(symbol_number)
                elif symbol_number == 0:
                    self.stargate.keyboard.queue_center_button()
                elif symbol_number == -1 and self.stargate.wormhole_active is False and len(self.stargate.address_buffer_outgoing) > 0:
                    # Abort dialing
                    self.stargate.dialing_log.dialing_fail(self.stargate.address_buffer_outgoing)
                    self.stargate.shutdown(cancel_sound=False, wormhole_fail_sound=False)

                data = { "success": True }

            elif self.path == "/do/clear_outgoing_buffer":
                self.stargate.shutdown(cancel_sound=False, wormhole_fail_sound=False)
                data = { "success": True }

            elif self.path == "/do/set_glyph_ring_zero":
                self.stargate.ring.zero_position()
                data = { "success": True }

            elif self.path == "/do/dhd_test_enable":
                self.stargate.keyboard.enable_dhd_test(True)
                data = { "success": True }

            elif self.path == "/do/dhd_test_disable":
                self.stargate.keyboard.enable_dhd_test(False)
                data = { "success": True }

            ##### UPDATE DATA HANDLERS BELOW ####
            elif self.path == '/update/local_stargate_address':

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

            elif self.path == '/update/subspace_ip':
                try:
                    self.stargate.subspace_client.set_ip_address(data['ip'])
                    data = { "success": True, "message": "Subspace IP Address Saved." }
                except ValueError as ex:
                    data = { "success": False, "message": str(ex) }

            elif self.path == '/update/config':
                try:
                    message = self.stargate.cfg.set_bulk(data)
                    data = { "success": True, "message": "Configuration Saved", "results": message }
                except (NameError, ValueError) as ex:
                    data = { "success": False, "message": str(ex) }

            else:
                # Unknown path, send 404
                self.send_response(404, 'Not Found')
                self.end_headers()
                return

            # If we have data, send it, else send a bare 200 OK
            if data:
                self.send_json_response(data)
            else:
                self.send_response(200, 'OK')
                self.end_headers()

            return

        except: # pylint: disable=bare-except
            if self.stargate.cfg.get("control_api_debug_enable"): # pylint: disable=no-member
                raise

            # Encountered an exception: send a 500
            self.send_response(500, "Exception")
            self.end_headers()

    def send_json_response(self, data):
        content = json.dumps( data )
        self.send_response(200, 'OK')
        self.send_header("Content-type", "text/json")
        self.end_headers()
        self.wfile.write(content.encode())
