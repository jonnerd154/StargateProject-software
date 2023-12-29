import os
import subprocess
from ipaddress import ip_address
import socket
from icmplib import ping
import netifaces

class NetworkTools:

    def __init__(self, log):

        self.cloudflare = '1.1.1.1'
        self.google = '8.8.8.8'

        self.log = log

    def has_internet_access(self): # was called check_internet_connection
        """
        This function checks cloudflare and google to see if there is an internet connection.
        :return: True if there is a connection to the internet, and false if not.
        """

        if 'open' in self.check_net(self.cloudflare):
            # self.log.log('We have Internet connection!')
            return True

        if 'open' in self.check_net(self.google):
            # self.log.log('We have Internet connection!')
            return True

        self.log.log('No Internet connection! Some features will not work!')
        return False

    @staticmethod
    def check_net(host):
        """
        A little helper that returns the output of the nc command, to check if there is net connection.
        :param host: the host to check
        :return: returns the output as seen if run in a shell.
        """
        return subprocess.run(['nc', host, '53', '-w', '3', '-zv'], capture_output=True, text=True, check=False).stderr # TODO: Check should be True/handled

    def get_ip(self, fqdn_or_ip):
        """
        This function takes a string as input and validates if the string is a valid IP address. If it is not a valid IP
        the function assumes it is a FQDN and tries to resolve the IP from the domain name. If this fails, it returns None
        :param fqdn_or_ip: A string of an IP or a FQDN
        :return: The IP address is returned as a string, or None is returned if it fails.
        """
        _ip_address = None
        try:
            _ip_address = ip_address(fqdn_or_ip)
            # print('yay, it is an IP')
        except ValueError:
            try:
                # print('NOPE, not an IP, getting IP from FQDN')
                _ip_address = socket.gethostbyname(fqdn_or_ip)
                # print('I found the IP:', ip)
            except ValueError:
                pass
        except Exception: # pylint: disable=broad-except
            self.log.log(f"Unable to determine IP address '{fqdn_or_ip}'")
            _ip_address = None
        return str(_ip_address)

    def get_local_ip(self):
        my_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # doesn't even have to be reachable
            my_sock.connect((self.google, 1))
            ret = my_sock.getsockname()[0]
        except socket.error:
            ret = '127.0.0.1'
        finally:
            my_sock.close()
        return ret

    def get_subspace_ip(self, subspace_only = False):
        # Try to get the IP from subspace
        subspace = self.get_ip_by_interface_list( ['subspace'] )
        if subspace:
            return subspace

        if not subspace_only:
            lan = self.get_ip_by_interface_list( [ 'wlan0', 'eth0', 'en0', 'en1' ] )
            if lan:
                return lan

        return None

    def get_ip_by_interface_list(self, interfaces):

        # Try to get the IP from each of the interfaces, in order. Return the first one.
        for interface in interfaces:
            result = self.get_ip_address_by_interface(interface)
            if result:
                return result

        return None

    def get_ip_address_by_interface(self, interface_name, do_ping = False, ping_ip=False):
        try:
            server_ip = netifaces.ifaddresses(interface_name)[2][0]['addr']
            if ip_address(server_ip):
                if do_ping:
                    self.ping(ping_ip)

                return server_ip
            return False
        except (KeyError, ValueError) as _ex:
            self.log.log(f'ERROR getting {interface_name} IP: {_ex}', True)
            return False

    @staticmethod
    def ping(ping_ip):
        if ping(ping_ip, count=1, timeout=1).is_alive:
            return True
        return False

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
        lan = self.get_ip_by_interface_list( [ 'wlan0', 'eth0', 'en0', 'en1' ] )
        if lan:
            return lan

        return None # If no IP found, return None
