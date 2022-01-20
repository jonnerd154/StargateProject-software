from ipaddress import ip_address
import socket
import subprocess
import os
import netifaces
from icmplib import ping

from database import Database

class SubspaceClient:

    def __init__(self, stargate):

        self.log = stargate.log
        self.cfg = stargate.cfg

        self.database = Database(stargate.base_path)

        self.logging = "normal"
        #self.logging = "verbose"

        # Retrieve the configurations
        self.port = self.cfg.get("subspace_port") # just for fun because the Stargate can stay open for 38 minutes. :)
        self.timeout = self.cfg.get("subspace_timeout") # the timeout value when connecting to a remote stargate (seconds)
        self.keep_alive_address = self.cfg.get("subspace_keep_alive_address")

        # Some other configurations that are relatively static will stay here
        self.header_bytes = 8
        self.encoding_format = 'utf-8'
        self.disconnect_message = '!DISCONNECT'

        # We'll share one Client object through a few methods. Initialize it here.
        self.client = None

    @staticmethod
    def get_public_key():
        try:
            cmd = 'sudo util/get_subspace_public_key.sh'
            return subprocess.check_output(cmd, shell=True).decode('ascii')
        except subprocess.CalledProcessError:
            return False

    def set_ip_address(self, subspace_ip):
        # Save it to the config so we can use it later
        self.cfg.set('subspace_ip_address', subspace_ip)

        # Update the WireGuard Config
        return self.configure_wireguard_ip(subspace_ip)

    def get_configured_ip(self):
        # Return the cached/local-config value (not from WireGuard/ifconfig)
        return self.cfg.get('subspace_ip_address')

    @staticmethod
    def configure_wireguard_ip(subspace_ip):
        try:
            cmd = f'sudo util/subspace_config-ip.sh {subspace_ip}'
            subprocess.check_output(cmd, shell=True).decode('ascii')
            return True
        except subprocess.CalledProcessError:
            return False

    def send_raw(self, msg):
        message = msg.encode(self.encoding_format)
        msg_length = len(message)
        send_length = str(msg_length).encode(self.encoding_format)
        send_length += b' ' * (self.header_bytes - len(send_length))
        self.client.send(send_length)
        self.client.send(message)

    def send_to_remote_stargate(self, server_ip, message_string):
        """
        This is the stargate client function. It is used to send messages to a Stargate server. It automatically sends the
        disconnect message after the message_string.
        :param server_ip: The IP of the stargate server where to send the message, as string.
        :param message_string: The message can be a string of stargate symbols. eg '[7]', '[7, 32]' or '[7, 32, 27, 18, 12, 16]'.
        It can also be, 'centre_button_incoming'.
        If the message is "what_is_your_status", we also expect a status message in return.
        :return: The function returns a tuple where the first value is True if we have a connection to the server, and False if not.
        The second value in the tuple is either None, or it contains the status of the remote gate, if we asked for it.
        """

        # If we don't have an IP, don't try to send anything
        if server_ip is None:
            return

        if self.logging == "verbose":
            self.log.log(f"send_to_remote_stargate( {server_ip}, {message_string} )")

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.settimeout(self.timeout) # set the timeout
        connection_to_server = False # TODO: get rid of this var
        remote_gate_status = None

        ## Try to establish a connection to the server.
        try:
            self.client.connect( (server_ip, self.port) )
            connection_to_server = True # TODO: Move the if block below into the try block, get rid of this var
        except socket.error as ex:
            self.log.log(f'Error sending to remote server -> {ex}')
            remote_gate_status = False
            return connection_to_server, remote_gate_status # return false if we do not have a connection.

        if connection_to_server:
            self.send_raw(message_string) # Send the message

            #If we ask for the status, expect an answer
            if message_string == 'what_is_your_status':
                remote_gate_status = (self.client.recv(8).decode(self.encoding_format))
                if self.logging == "verbose":
                    self.log.log(f'Received STATUS REPLY Line 107: {remote_gate_status}')

            self.send_raw(self.disconnect_message) # always disconnect.
            return True, remote_gate_status

        return False, False

    def get_status_of_remote_gate(self, remote_ip):
        """
        This helper functions tries to determine if the wormhole of the remote gate is already active, or if we are currently dialing out.
        :param remote_ip: The IP address of the remote gate
        :return: True if a wormhole is already established and False if not.
        """
        status = self.send_to_remote_stargate(remote_ip, 'what_is_your_status')
        if status[1] == 'False':
            return False
        return True

    def get_stargate_server_ip(self):
        """
        This method tries to get the IP address of the subspace network interface. It also tries to start the subspace
        interface if it's not already present. If it can't get the subspace interface IP, it will try to get the wlan0 IP instead.
        :return: The IP address is returned as a string.
        """

        ## If the subspace interface is not active, try to activate it.
        if not 'subspace' in netifaces.interfaces():
            try:
                self.log.log('Subspace network interface was not found, attempting to bring up the interface.')
                os.popen('wg-quick up subspace').read()
            except (IndexError, KeyError) as ex:
                self.log.log(f'subspace ERROR: {ex}')

        # Try to get the IP from subspace
        subspace = self.get_ip_address_by_interface('subspace')
        if subspace:
            return subspace

        # Try to get the IP from wlan0
        lan = self.get_lan_ip()
        if lan:
            return lan

        return None # If no IP found, return None

    # TODO: Move to NetTools
    def get_lan_ip(self):
        # TODO: Refactor to loop over a list of interface names

        # Try to get the IP from wlan0
        wlan0 = self.get_ip_address_by_interface('wlan0')
        if wlan0:
            return wlan0

        # Try to get the IP from eth0
        eth0 = self.get_ip_address_by_interface('eth0')
        if eth0:
            return eth0

        # Try to get the IP from en0
        en0 = self.get_ip_address_by_interface('en0')
        if en0:
            return en0

        # Try to get the IP from en1 (MacOS)
        en1 = self.get_ip_address_by_interface('en1')
        if en1:
            return en1

        return None

    # TODO: Move to NetTools
    def get_subspace_ip(self, subspace_only = False):
        # Try to get the IP from subspace
        subspace = self.get_ip_address_by_interface('subspace')
        if subspace:
            return subspace

        if not subspace_only:
            lan = self.get_lan_ip()
            if lan:
                return lan

        return None

    # TODO: Move to NetTools?
    def get_ip_address_by_interface(self, interface_name, do_ping = False):
        try:
            server_ip = netifaces.ifaddresses(interface_name)[2][0]['addr']
            if ip_address(server_ip):
                if do_ping:
                    self.ping()

                return server_ip
            return False
        except (KeyError, ValueError) as _ex:
            self.log.log('ERROR getting {interface_name} IP: {_ex}', True)
            return False

    def is_online(self):
        return self.ping()

    def ping(self):
        if ping(self.keep_alive_address, count=1, timeout=1).is_alive:
            return True
        return False
