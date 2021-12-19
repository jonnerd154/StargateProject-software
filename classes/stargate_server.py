import socket
from threading import Thread
from time import sleep
from icmplib import ping

from stargate_address_manager import StargateAddressValidator
from database import Database

class StargateServer:
    """
    This Class starts a stargate server to listen for incoming connections. The server runs on port 3838. It tries to setup the server on
    the subspace interface. Failing that, it will use the wlan0 interface instead. Failing that it will use the eth0 interface.
    The Stargate server is run in "parallel" in its own thread.
    :return: Nothing is returned.
    """
    def __init__(self, stargate):

        self.stargate = stargate
        self.log = stargate.log
        self.cfg = stargate.cfg
        self.base_path = stargate.base_path
        self.subspace = stargate.subspace
        self.addrManager = stargate.addrManager
        self.addressBook = stargate.addrManager.getBook()

        self.database = Database(self.base_path)
        
        # Retrieve the configurations
        self.port = self.cfg.get("subspace_port") # I chose 3838 because the Stargate can stay open for 38 minutes. :)  
        self.keep_alive_interval = self.cfg.get("subspace_keep_alive_interval")
        self.keep_alive_address = self.cfg.get("subspace_keep_alive_address")

        # Some other configurations that are relatively static will stay here
        self.header = 8
        self.encoding_format = 'utf-8'
        self.disconnect_message = '!DISCONNECT'
        self.keep_alive_running_check_interval = 0.5

        # Get server IP, preferable the IP of the stargate in subspace.
        self.server_ip = self.subspace.get_stargate_server_ip()
        self.server_address = (self.server_ip, self.port)
        
        # Configure the socket, open/bind
        self.open_socket()

        # Start a thread to keep the subspace connection alive. It's most likely not needed, but might help connections to establish faster.
        thread_keep_alive = Thread(target=self.keep_alive, args=(self.keep_alive_address, self.keep_alive_interval, self.stargate ))
        thread_keep_alive.start()

        # Update fan_gates from the subspace server
        self.stargate.addrManager.update_fan_gates_from_db()


    def open_socket(self):
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind(self.server_address)

    def keep_alive(self, IP_address, interval, stargate):
        """
        This functions simply sends a ping to the specified IP address every specified interval
        :param stargate: The stargate object.
        :param IP_address: the IP address as a string
        :param interval: the interval for each ping as an int in second. (the sleep time)
        :return: Nothing is returned
        """

        time_since_last_ping = 0
        while stargate.running:

            sleep(self.keep_alive_running_check_interval)

            if (time_since_last_ping >= self.keep_alive_interval):
                #self.log.log("Sending keepalive ping")
                ping(IP_address, count=1, timeout=1)
                time_since_last_ping = 0
            else:
                time_since_last_ping+=self.keep_alive_running_check_interval

    def handle_incoming_wormhole(self, conn, addr):
        connected = True  # while there is a connection from another gate.
        while connected:
            msg_length = conn.recv(self.header).decode(self.encoding_format)
            if msg_length:  # if the msg_length is not None
                msg_length = int(msg_length)
                msg = conn.recv(msg_length).decode(self.encoding_format)
                if msg == self.disconnect_message:  # always disconnect after sending a message to the server.
                    connected = False

                # If we are receiving the centre_button_incoming
                elif msg == 'centre_button_incoming':
                    # If a wormhole is already established, and we are receiving the centre_button_incoming from the same gate.
                    if self.stargate.wormhole and addr[0] == self.stargate.fan_gate_incoming_IP:
                        self.stargate.centre_button_incoming = False
                        self.stargate.wormhole = False
                    # If we are dialling (no wormhole established)
                    else:
                        self.stargate.centre_button_incoming = True
                        # If there are not already a saved IP, or if we dialed an none fan_gate
                        if not self.stargate.fan_gate_incoming_IP:
                            self.stargate.fan_gate_incoming_IP = addr[0] # Save the IO address when establishing a wormhole.
                            self.stargate.dialer.hardware.set_center_on()# Activate the centre_button_outgoing light

                    planet_name = self.subspace.get_planet_name_from_IP(addr[0], self.addressBook.get_fan_gates())
                    stargate_address = self.subspace.get_stargate_address_from_IP(addr[0], self.addressBook.get_fan_gates())
                    self.log.log('1 Received from {} - {} -> {}'.format(planet_name, stargate_address, msg))

                # If we are asked about the status (wormhole already active from a different gate or actively dialing out)
                elif msg == 'what_is_your_status':
                    # self.log.log('Received from {} -> {}'.format(addr, msg))
                    # It the wormhole is already established, or if we are dialing out.
                    if self.stargate.wormhole or len(self.stargate.address_buffer_outgoing) > 0:
                        # If the established wormhole is from the remote gate
                        if addr[0] == self.stargate.fan_gate_incoming_IP:
                            status = False
                        else:
                            status = True
                    else:
                        status = False
                    # Send the status to the client stargate
                    conn.send(str(status).encode(self.encoding_format))

                # If we are receiving a stargate address, add it to the incoming buffer.
                elif self.addrManager.is_valid(msg):
                    address = self.addrManager.is_valid(msg)
                    for symbol in address:
                        if not symbol in self.stargate.address_buffer_incoming:
                            self.stargate.address_buffer_incoming.append(symbol)

                    planet_name = self.subspace.get_planet_name_from_IP(addr[0], self.addressBook.get_fan_gates())
                    stargate_address = self.subspace.get_stargate_address_from_IP(addr[0], self.addressBook.get_fan_gates())
                    self.log.log('2 Received from {} - {} -> {}'.format(planet_name, stargate_address, msg))

                # For unknown messages
                else:
                    stargate_address = self.subspace.get_stargate_address_from_IP(addr[0], self.addressBook.get_fan_gates())
                    self.log.log('Received UNKNOWN MESSAGE from {} - {} -> {}     But I do not know what to do with that!'.format(addr[0], stargate_address, msg))
        conn.close()  # close the connection.
    def start(self):
        if self.server_ip: # If we have found an IP to use for the server.
            self.server.listen()
            self.log.log('Listening for incoming wormholes on {}:{}'.format(self.server_ip, self.port))

            while True:
                conn, addr = self.server.accept()
                handle_incoming_wormhole_thread = Thread(target=self.handle_incoming_wormhole, args=(conn, addr))
                handle_incoming_wormhole_thread.start()
        else:
            self.log.log('Unable to start the Stargate server, no IP address found')
