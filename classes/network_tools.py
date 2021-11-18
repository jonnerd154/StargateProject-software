import subprocess

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
