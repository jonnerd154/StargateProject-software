from database import Database

class Subspace:

    def __init__(self, stargate):
        
        self.log = stargate.log
        self.cfg = stargate.cfg
        
        self.database = Database()
        
        
    def send_raw(self, msg):
        message = msg.encode(encoding_format)
        msg_length = len(message)
        send_length = str(msg_length).encode(encoding_format)
        send_length += b' ' * (header - len(send_length))
        client.send(send_length)
        client.send(message)

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
        import socket
        header = 8
        port = 3838 # just for fun because the Stargate can stay open for 38 minutes. :)
        encoding_format = 'utf-8'
        disconnect_message = '!DISCONNECT'
        server_ip = server_ip
        server_address = (server_ip, port)
        timeout = 10 # the timeout value when connecting to a remote stargate (seconds)
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(timeout) # set the timeout
        connection_to_server = False
        remote_gate_status = None

        ## Try to establish a connection to the server.
        try:
            client.connect(server_address)
            connection_to_server = True
        except Exception as ex:
            print (ex)
            log('sg1.log', f'Error sending to remote server -> {ex}')
            return connection_to_server, remote_gate_status # return false if we do not have a connection.

        if connection_to_server:
            self.send_raw(message_string) # Send the message

            #If we ask for the status, expect an answer
            if message_string == 'what_is_your_status':
                remote_gate_status = (client.recv(8).decode(encoding_format))

            self.send(disconnect_message) # always disconnect.
            return True, remote_gate_status

    def get_ip_from_stargate_address(self, stargate_address, known_fan_made_stargates):
        """
        This functions gets the IP address from the first two symbols in the gate_address. The first two symbols of the
        fan_gates are always unique.
        :param stargate_address: This is the destination for which to match with an IP.
        :param known_fan_made_stargates: This is the dictionary of the known stargates
        :return: The IP address is returned as a string.
        """
        for gate in known_fan_made_stargates:
            if len(stargate_address) > 1 and stargate_address[0:2] == known_fan_made_stargates[gate][0][0:2]:
                return  known_fan_made_stargates[gate][1]
        else:
            print( 'Unable to get IP for', stargate_address)

    def get_stargate_address_from_IP(self, ip, fan_gates_dictionary):
        """
        This function simply gets the stargate address that matches the IP address
        :param ip: the IP address as a string
        :param fan_gates_dictionary: A dictionary of stargates (most likely from the database of known stargate)
        :return: The stargate address is returned as a string.
        """
        stargate_ip = 'Unknown'
        for stargate in fan_gates_dictionary:
            if fan_gates_dictionary[stargate][1] == ip:
                return fan_gates_dictionary[stargate][0]
        return str(stargate_ip) # If the gate address of the IP was not found
    
    def get_status_of_remote_gate(self, remote_ip):
        """
        This helper functions tries to determine if the wormhole of the remote gate is already active, or if we are currently dialing out.
        :param remote_ip: The IP address of the remote gate
        :return: True if a wormhole is already established and False if not.
        """
        status = send_to_remote_stargate(remote_ip, 'what_is_your_status')
        if status[1] == 'False':
            return False
        else:
            return True

    def get_planet_name_from_IP(self, IP, fan_gates):
        """
        This function gets the planet name of the IP in the fan_gate dictionary.
        :param fan_gates: The dictionary of fan_gates from the database
        :param IP: the IP address as a string
        :return: The planet/stargate name is returned as a string.
        """
        try:
            return [k for k, v in fan_gates.items() if v[1] == IP][0]
        except:
            return 'Unknown'

