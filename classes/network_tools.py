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

        # noinspection PyTypeChecker
        if 'succeeded' in self.check_net(self.cloudflare):
            # self.log.log('We have Internet connection!')
            return True
        elif 'succeeded' in self.check_net(self.google):
            # self.log.log('We have Internet connection!')
            return True
        else:
            self.log.log('No Internet connection! Some features will not work!')
            return False

    def check_net(self, host):
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
        ip = None
        try:
            ip = ip_address(fqdn_or_ip)
            # print('yay, it is an IP')
        except ValueError:
            try:
                # print('NOPE, not an IP, getting IP from FQDN')
                ip = socket.gethostbyname(fqdn_or_ip)
                # print('I found the IP:', ip)
            except:
                pass
        except:
            self.log.log("Unable to determine IP address '{}'".format(fqdn_or_ip))
            ip = None
        return str(ip)
    
    def get_local_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # doesn't even have to be reachable
            s.connect((self.google, 1))
            IP = s.getsockname()[0]
        except Exception:
            IP = '127.0.0.1'
        finally:
            s.close()
        return IP