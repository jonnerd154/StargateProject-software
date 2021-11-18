class Subspace:

	def __init__(self):
		pass
		
	def send_to_remote_stargate(server_ip, message_string):
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

    def send(msg):
        message = msg.encode(encoding_format)
        msg_length = len(message)
        send_length = str(msg_length).encode(encoding_format)
        send_length += b' ' * (header - len(send_length))
        client.send(send_length)
        client.send(message)

    ## Try to establish a connection to the server.
    try:
        client.connect(server_address)
        connection_to_server = True
    except Exception as ex:
        print (ex)
        log('sg1.log', f'Error sending to remote server -> {ex}')
        return connection_to_server, remote_gate_status # return false if we do not have a connection.

    if connection_to_server:
        send(message_string) # Send the message

        #If we ask for the status, expect an answer
        if message_string == 'what_is_your_status':
            remote_gate_status = (client.recv(8).decode(encoding_format))

        send(disconnect_message) # always disconnect.
        return True, remote_gate_status


def get_ip_from_stargate_address(stargate_address, known_fan_made_stargates):
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


def get_stargate_address_from_IP(ip, fan_gates_dictionary):
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


def get_ip(fqdn_or_ip):
    """
    This function takes a string as input and validates if the string is a valid IP address. If it is not a valid IP
    the function assumes it is a FQDN and tries to resolve the IP from the domain name. If this fails, it returns None
    :param fqdn_or_ip: A string of an IP or a FQDN
    :return: The IP address is returned as a string, or None is returned if it fails.
    """
    from ipaddress import ip_address
    from socket import gethostbyname
    ip = None
    try:
        ip = ip_address(fqdn_or_ip)
        # print('yay, it is an IP')
    except ValueError:
        try:
            # print('NOPE, not an IP, getting IP from FQDN')
            ip = gethostbyname(fqdn_or_ip)
            # print('I found the IP:', ip)
        except:
            pass
    except:
        print('total failure..')
        ip = None
    return str(ip)


def get_fan_gates_from_db(hard_coded_fan_gates_dictionary):
    """
    This function gets the fan_gates from the database and merges it with the hard_coded fan_gates dictionary
    :param hard_coded_fan_gates_dictionary: The dictionary containing any hard coded fan_gates not in the database, or a local gate perhaps
    :return: The updated fan_gate dictionary is returned.
    """
    import pymysql, dbinfo, ast
    from base64 import b64decode
    db = pymysql.connect(host=dbinfo.db_host, user=dbinfo.db_user, password=str(b64decode(dbinfo.db_pass), 'utf-8'), database=dbinfo.db_name)
    cursor = db.cursor()
    sql = f"SELECT * FROM `fan_gates`"
    cursor.execute(sql)
    db_fan_gates = cursor.fetchall()
    db.close()
    for gate in db_fan_gates:
        hard_coded_fan_gates_dictionary[gate[0]] = [ast.literal_eval(gate[1]), get_ip(gate[2])]
    return hard_coded_fan_gates_dictionary


def get_status_of_remote_gate(remote_ip):
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


def get_planet_name_from_IP(IP, fan_gates):
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


def keep_alive(IP_address, interval, stargate_object):
    """
    This functions simply sends a ping to the specified IP address every specified interval
    :param stargate_object: The stargate object.
    :param IP_address: the IP address as a string
    :param interval: the interval for each ping as an int in second. (the sleep time)
    :return: Nothing is returned
    """
    from icmplib import ping
    from time import sleep
    while stargate_object.running:
        sleep(interval)
        ping(IP_address, count=1, timeout=1)

def is_it_a_known_fan_made_stargate(dialed_address, known_fan_made_stargates, stargate_object):
    """
    This helper function tries to check the first two symbols in the dialled address and compares it to
    the known_fan_made_stargates to check if the address dialled is a known fan made stargate. The first two symbols
    is enough to determine if it's a fan_gate. The fan gates, need only two unique symbols for identification.
    :param stargate_object: The stargate object. This is used to rule out self dialling.
    :param dialed_address: a stargate address. It does not need to be complete. eg: [10, 15, 8, 24]
    :param known_fan_made_stargates: This is a dictionary of known stargates. eg:
            {'Kristian Tysse': [[7, 32, 27, 18, 12, 16], '192.168.10.129'],
            'Someone else': [[7, 32, 27, 18, 12, 16], '1.2.3.4']
            }
    :return: True if we are dialing a fan made address, False if not.
    """
    for gate in known_fan_made_stargates:
        try:
            #If we dial our own local address:
            if dialed_address[:2] == stargate_object.local_stargate_address[:2]:
                return False
            # If we dial a known fan_gate
            elif dialed_address[:2] == known_fan_made_stargates[gate][0][:2]:
                return True
        except:
            pass
    return False
