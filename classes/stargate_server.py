import socket
import os, netifaces
from threading import Thread
from time import sleep
from ipaddress import ip_address
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

        self.thread = Thread

        self.stargate = stargate
        self.log = stargate.log
        self.cfg = stargate.cfg
        self.base_path = stargate.base_path

        self.database = Database(self.base_path)

        #TODO: move some of this to config.json
        self.header = 8
        self.port = 3838  # I chose 3838 because the Stargate can stay open for 38 minutes. :)
        self.encoding_format = 'utf-8'
        self.disconnect_message = '!DISCONNECT'
        self.keep_alive_address = '172.30.0.1'
        self.keep_alive_interval = 24
        self.keep_alive_running_check_interval = 0.5

        # Get server IP, preferable the IP of the stargate in subspace.
        self.server_ip = self.get_stargate_server_ip()
        self.server_address = (self.server_ip, self.port)
        
        # Configure the socket, open/bind
        self.open_socket()

        # Start a thread to keep the subspace connection alive. It's most likely not needed, but might help connections to establish faster.
        thread_keep_alive = self.thread(target=self.keep_alive, args=(self.keep_alive_address, self.keep_alive_interval, self.stargate ))
        thread_keep_alive.start()

        # Keep the known fan_gates here.
        self.known_fan_gates = self.stargate.addrManager.update_fan_gates_from_db()


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
                self.log.log("Sending keep alive ping")
                ping(IP_address, count=1, timeout=1)
                time_since_last_ping = 0
            else:
                time_since_last_ping+=self.keep_alive_running_check_interval

    def get_stargate_server_ip(self):
        """
        This method tries to get the IP address of the subspace network interface. It also tries to start the subspace
        interface if it's not already present. If it can't get the subspace interface IP, it will try to get the wlan0 IP instead.
        :return: The IP address is returned as a string.
        """

        server_ip = None  # initialize the variable

        ## If the subspace interface is not active, try to activate it.
        if not 'subspace' in netifaces.interfaces():
            try:
                self.log.log('Subspace network interface was not found, attempting to bring up the interface.')
                os.popen('wg-quick up subspace').read()
            except Exception as ex:
                self.log.log('subspace ERROR: {}'.format(ex))

        ## Try to get IP from subspace
        if 'subspace' in netifaces.interfaces():
            try:
                server_ip = netifaces.ifaddresses('subspace')[2][0]['addr']
                if ip_address(server_ip):
                    ping(self.keep_alive_address, count=1, timeout=1) # ping the gateway creating some traffic signaling subspace that you are here.
                    return server_ip
            except Exception as ex:
                self.log.log('ERROR getting subspace IP: {}'.format(ex))

        # Try to get the IP from wlan0
        if 'wlan0' in netifaces.interfaces():
            try:
                server_ip = netifaces.ifaddresses('wlan0')[2][0]['addr']
                if ip_address(server_ip):
                    return server_ip
            except Exception as ex:
                self.log.log('ERROR getting wlan0 IP: {}'.format(ex))

        # Try to get the IP from eth0
        if 'eth0' in netifaces.interfaces():
            try:
                server_ip = netifaces.ifaddresses('eth0')[2][0]['addr']
                if ip_address(server_ip):
                    return server_ip
            except Exception as ex:
                self.log.log('ERROR getting eth0 IP: {}'.format(ex))
        return server_ip # returns None if no ip was found

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

                    planet_name = self.get_planet_name_from_IP(addr[0], self.known_fan_gates)
                    stargate_address = self.get_stargate_address_from_IP(addr[0], self.known_fan_gates)
                    self.log.log('Received from {} - {} -> {}'.format(planet_name, stargate_address, msg))

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
                elif self.validate_string_as_stargate_address(msg):
                    address = self.validate_string_as_stargate_address(msg)
                    for symbol in address:
                        if not symbol in self.stargate.address_buffer_incoming:
                            self.stargate.address_buffer_incoming.append(symbol)

                    planet_name = self.get_planet_name_from_IP(addr[0], self.known_fan_gates)
                    stargate_address = self.get_stargate_address_from_IP(addr[0], self.known_fan_gates)
                    self.log.log('Received from {} - {} -> {msg}'.format(planet_name, stargate_address))

                # For unknown messages
                else:
                    stargate_address = self.get_stargate_address_from_IP(addr[0], self.known_fan_gates)
                    self.log.log('Received UNKNOWN MESSAGE from {} - {} -> {} \t But I do not know what to do with that!'.format(addr[0], stargate_address, msg))
        conn.close()  # close the connection.
    def start(self):
        if self.server_ip: # If we have found an IP to use for the server.
            self.server.listen()
            self.log.log('Listening for incoming wormholes on {}:{}'.format(self.server_ip, self.port))

            while True:
                conn, addr = self.server.accept()
                handle_incoming_wormhole_thread = self.thread(target=self.handle_incoming_wormhole, args=(conn, addr))
                handle_incoming_wormhole_thread.start()
        else:
            self.log.log('Unable to start the Stargate server, no IP address found')
