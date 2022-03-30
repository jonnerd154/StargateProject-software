import socket
from threading import Thread
from time import sleep
from icmplib import ping

import subspace_messages

class SubspaceServer:
    """
    This Class starts a subspace server to listen for incoming connections. The server runs on port 3838. It tries to setup the server on
    the subspace interface. Failing that, it will use the wlan0 interface instead. Failing that it will use the eth0 interface.
    The Stargate server is run in "parallel" in its own thread.
    :return: Nothing is returned.
    """
    def __init__(self, stargate):

        self.stargate = stargate
        self.log = stargate.log
        self.cfg = stargate.cfg
        self.base_path = stargate.base_path
        self.subspace_client = stargate.subspace_client
        self.addr_manager = stargate.addr_manager
        self.address_book = stargate.addr_manager.get_book()

        self.logging = "normal"
        #self.logging = "verbose"

        # Retrieve the configurations
        self.port = self.cfg.get("subspace_port") # I chose 3838 because the Stargate can stay open for 38 minutes. :)
        self.keep_alive_interval = self.cfg.get("subspace_keep_alive_interval")
        self.keep_alive_address = self.cfg.get("subspace_keep_alive_address")

        # Some other configurations that are relatively static will stay here
        self.header = 8
        self.encoding_format = 'utf-8'
        self.keep_alive_running_check_interval = 0.5

        # Get server IP, preferable the IP of the stargate in subspace.
        self.server_ip = "0.0.0.0" #self.subspace_client.get_stargate_server_ip()
        self.server_address = (self.server_ip, self.port)

        # Configure the socket, open/bind
        self.open_socket()

        # Start a thread to keep the subspace connection alive. It's most likely not needed, but might help connections to establish faster.
        thread_keep_alive = Thread(target=self.keep_alive, args=(self.keep_alive_address, self.stargate ))
        thread_keep_alive.start()

        # Update fan_gates from the subspace server
        if self.cfg.get("fan_gate_refresh_enable"):
            self.stargate.addr_manager.update_fan_gates_from_api()

    def open_socket(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(self.server_address)

    def keep_alive(self, remote_addr, stargate):
        """
        This functions simply sends a ping to the specified IP address every specified interval
        :param stargate: The stargate object.
        :param remote_addr: the IP address as a string
        :return: Nothing is returned
        """

        # TODO: Use schedule

        if self.logging == "verbose":
            self.log.log('Sending Keepalive')

        time_since_last_ping = 0
        while stargate.running:

            sleep(self.keep_alive_running_check_interval)

            if time_since_last_ping >= self.keep_alive_interval:
                #self.log.log("Sending keepalive ping")
                ping(remote_addr, count=1, timeout=1)
                time_since_last_ping = 0
            else:
                time_since_last_ping+=self.keep_alive_running_check_interval

    def handle_incoming_wormhole(self, conn, addr):
        if self.logging == "verbose":
            self.log.log(f'handle_incoming_wormhole({conn}, {addr}')

        stargate_address = self.addr_manager.get_stargate_address_from_ip(addr[0])

        connected = True  # while there is a connection from another gate.
        while connected:
            if self.logging == "verbose":
                self.log.log('connected loop')

            msg_length = conn.recv(self.header).decode(self.encoding_format)
            if msg_length:  # if the msg_length is not None
                msg_length = int(msg_length)
                msg = conn.recv(msg_length).decode(self.encoding_format)
                if msg == subspace_messages.DISCONNECT:  # always disconnect after sending a message to the server.
                    if self.logging == "verbose":
                        self.log.log('disconnect request')
                    connected = False

                # If we are receiving the centre_button_incoming
                elif msg == subspace_messages.DIAL_CENTER_INCOMING:
                    if self.logging == "verbose":
                        self.log.log('centre_button_incoming')
                    # Check if incoming wormholes are allowed
                    if not self.cfg.get("dialing_incoming_allowed"):
                        conn.close()  # close the connection.
                        return

                    # If a wormhole is already established, and we are receiving DIAL_CENTER_INCOMING from the same gate.
                    if self.stargate.wormhole_active and addr[0] == self.stargate.fan_gate_incoming_ip:
                        self.stargate.centre_button_incoming = False
                        self.stargate.wormhole_active = False
                    # If we are dialling (no wormhole established)
                    else:
                        self.log.log("Received Center Button Incoming")
                        self.stargate.centre_button_incoming = True
                        # If there are not already a saved IP, or if we dialed an none fan_gate
                        if not self.stargate.fan_gate_incoming_ip:
                            self.stargate.fan_gate_incoming_ip = addr[0] # Save the IO address when establishing a wormhole.

                    planet_name = self.addr_manager.get_planet_name_from_ip(addr[0])
                    if self.logging == "verbose":
                        self.log.log(f'Line 123: Received from {planet_name} - {stargate_address} -> {msg}')

                # If we are asked about the status (wormhole already active from a different gate or actively dialing out)
                elif msg == subspace_messages.CHECK_STATUS:
                    # If the wormhole is already established, or if we are dialing out.
                    if self.stargate.wormhole_active or len(self.stargate.address_buffer_outgoing) > 0:
                        # If the established wormhole is from the remote gate
                        if addr[0] == self.stargate.fan_gate_incoming_ip:
                            status = False
                        else:
                            status = True
                    else:
                        status = False

                    self.log.log(f'Received CHECK_STATUS from {addr} is_busy -> {status}')

                    # Send the status to the client stargate
                    conn.send(str(status).encode(self.encoding_format))

                # If we are receiving a stargate address, add it to the incoming buffer.
                elif self.addr_manager.is_valid(msg):

                    # Check if incoming wormholes are allowed
                    if not self.cfg.get("dialing_incoming_allowed"):
                        conn.close()  # close the connection.
                        return

                    address = self.addr_manager.is_valid(msg)
                    for symbol in address:
                        if not symbol in self.stargate.address_buffer_incoming:
                            self.stargate.address_buffer_incoming.append(symbol)

                    planet_name = self.addr_manager.get_planet_name_from_ip(addr[0])
                    if self.logging == "verbose":
                        self.log.log(f'Received Address Components from {planet_name} - {stargate_address} -> {msg}')

                # For unknown messages
                else:
                    self.log.log(f'Received UNKNOWN MESSAGE from {addr[0]} - {stargate_address} -> {msg}')

        conn.close()  # close the connection.

    def start(self):
        if self.server_ip: # If we have found an IP to use for the server.
            self.server.listen()
            self.log.log(f'Listening for incoming wormholes on {self.server_ip}:{self.port}')

            while True:
                conn, addr = self.server.accept()
                handle_incoming_wormhole_thread = Thread(target=self.handle_incoming_wormhole, args=(conn, addr))
                handle_incoming_wormhole_thread.start()
        else:
            self.log.log('Unable to start the Stargate server, no IP address found')
