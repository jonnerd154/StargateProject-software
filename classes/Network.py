class NetworkTools:

	def __init__(self):
		pass

	def has_internet_access(self): # was called check_internet_connection
    """
    This function checks cloudflare and google to see if there is an internet connection.
    :return: True if there is a connection to the internet, and false if not.
    """
    import subprocess
    cloudflare = '1.1.1.1'
    google = '8.8.8.8'
    def check_net(host):
        """
        A little helper that returns the output of the nc command, to check if there is net connection.
        :param host: the host to check
        :return: returns the output as seen if run in a shell.
        """
        return subprocess.run(['nc', host, '53', '-w', '3', '-zv'], capture_output=True, text=True).stderr

    # noinspection PyTypeChecker
    if 'succeeded' in check_net(cloudflare):
        # log('sg1.log', 'We have Internet connection!')
        return True
    elif 'succeeded' in check_net(google):
        # log('sg1.log', 'We have Internet connection!')
        return True
    else:
        log('sg1.log', 'No Internet connection! Some features will not work!')
        return False
