import subprocess
from ipaddress import ip_address
import socket

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

        if 'succeeded' in self.check_net(self.cloudflare):
            # self.log.log('We have Internet connection!')
            return True

        if 'succeeded' in self.check_net(self.google):
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
        return subprocess.run(['nc', host, '53', '-w', '3', '-zv'], capture_output=True, text=True).stderr

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
        except Exception: # TODO: use specific Exception type
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
