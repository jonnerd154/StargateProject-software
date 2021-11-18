"""
This file contains some helpful functions used throughout the stargate program.
"""
import os
def play_random_audio_clip(path_to_folder):
    from os import listdir, path
    from random import choice
    import simpleaudio as sa
    """
    This function plays a random audio clip from the specified folder path. Must include trailing slash.
    :param path_to_folder: The path to the folder containing the audio clips as a string, including the trailing slash.
    :return: the play object is returned.
    """
    rand_file = choice(listdir(path_to_folder))
    filepath =  path.join(path_to_folder, rand_file)

    while not path.isfile(filepath): # If the rand_file is not a file. (If it's a directory)
        rand_file = choice(listdir(path_to_folder)) # Choose a new one.
        filepath = path.join(path_to_folder, rand_file) # Update Filepath
    random_audio = sa.WaveObject.from_wave_file(path_to_folder + '/' + rand_file)
    return random_audio.play()
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
def log(file, string_for_logging):
    """
    This functions logs the string_for_logging to the end of file.
    :param file: the file name as a string. It will be placed in the same folder as the file from where this function is run.
    :param string_for_logging: the entry for the log, as a string. The timestamp will be prepended automatically.
    :return: Nothing is returned.
    """
    import pwd, grp
    from os import stat
    from pathlib import Path
    from datetime import datetime
    root_path = Path(__file__).parent.absolute()
    with open(Path.joinpath(root_path, file), 'a') as sg1log:
        sg1log.write('\n' + f'[{datetime.now().replace(microsecond=0)}] \t {string_for_logging}')
    ## If the owner and group of the file is wrong, fix it.
    # get the user ID and group ID of the owner of this file (__file__). (In most instances this would result in the UID 1001 for the sg1 user.
    uid = pwd.getpwnam(pwd.getpwuid(stat(__file__).st_uid).pw_name).pw_uid
    gid = grp.getgrnam(pwd.getpwuid(stat(__file__).st_uid).pw_name).gr_gid
    if stat(Path.joinpath(root_path, file)).st_uid != uid: # If the user is wrong
        os.chown(str(root_path / file), uid, gid) # Change the owner and group of the file.
def key_press():
    """
    This helper function stops the program (thread) and waits for a single keypress.
    :return: The pressed key is returned.
    """
    import sys, tty, termios
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch
def ask_for_input(stargate_object):
    """
    This function takes the stargate_object as input and listens for user input (from the DHD or keyboard). The pressed key
    is converted to a stargate symbol number as seen in this document: https://www.rdanderson.com/stargate/glyphs/index.htm
    This function is run in parallel in its own thread.
    :param stargate_object: The stargate object itself.
    :return: Nothing is returned, but the stargate_object is manipulated.
    """
    from pathlib import Path
    root_path = Path(__file__).parent.absolute()

    ## the dictionary containing the key to symbol-number relations.
    key_symbol_map = {'8': 1, 'C': 2, 'V': 3, 'U': 4, 'a': 5, '3': 6, '5': 7, 'S': 8, 'b': 9, 'K': 10, 'X': 11, 'Z': 12,
                      'E': 14, 'P': 15, 'M': 16, 'D': 17, 'F': 18, '7': 19, 'c': 20, 'W': 21, '6': 22, 'G': 23, '4': 24,
                      'B': 25, 'H': 26, 'R': 27, 'L': 28, '2': 29, 'N': 30, 'Q': 31, '9': 32, 'J': 33, '0': 34, 'O': 35,
                      'T': 36, 'Y': 37, '1': 38, 'I': 39
                      }

    print("Listening for input from the DHD. You can abort with the '-' key.")
    while True: # Keep running and ask for user input
        key = key_press() #Save the input key as a variable
        ## Convert the key to the correct symbol_number. ##
        try:
            symbol_number = key_symbol_map[key]  # convert key press to symbol_number
        except KeyError:  # if the pressed button is not a key in the self.key_symbol_map dictionary
            symbol_number = 'unknown'
            if key == '-':
                symbol_number = 'abort'
            if key == 'A':
                symbol_number = 'centre_button_outgoing'

        play_random_audio_clip(str(root_path / "soundfx/DHD/"))
        log('sg1.log', f'key: {key} -> symbol: {symbol_number}')

        ## If the user inputs the - key to abort. Not possible from the DHD.
        if key == '-':
            stargate_object.running = False # Stop the stargate object from running.
            break # This will break us out of the while loop and end the function.

        ## If the user hits the centre_button
        elif key == 'A':
            # If we are dialling
            if len(stargate_object.address_buffer_outgoing) > 0 and not stargate_object.wormhole:
                stargate_object.centre_button_outgoing = True
                stargate_object.dhd.setPixel(0, 255, 0, 0) # Activate the centre_button_outgoing light
                stargate_object.dhd.latch()
            # If an outgoing wormhole is established
            if stargate_object.wormhole == 'outgoing':
                if stargate_object.fan_gate_online_status: # If we are connected to a fan_gate
                    send_to_remote_stargate(get_ip_from_stargate_address(stargate_object.address_buffer_outgoing, stargate_object.fan_gates), 'centre_button_incoming')
                if not stargate_object.black_hole: # If we did not dial the black hole.
                    stargate_object.wormhole = False # cancel outgoing wormhole

        # If we are hitting symbols on the DHD.
        elif symbol_number != 'unknown' and symbol_number not in stargate_object.address_buffer_outgoing:
            # If we have not yet activated the centre_button
            if not (stargate_object.centre_button_outgoing or stargate_object.centre_button_incoming):
                ### DHD lights ###
                stargate_object.dhd.setPixel(symbol_number, 250, 117, 0)
                stargate_object.dhd.latch()
                stargate_object.address_buffer_outgoing.append(symbol_number)
                print(stargate_object.address_buffer_outgoing) # Output the address_buffer
                log('sg1.log', f'address_buffer_outgoing: {stargate_object.address_buffer_outgoing}') # Log the address_buffer
def validate_string_as_stargate_address(input_address):
    """
    This is just a simple helper function to check if the input is indeed a representation of a stargate address.
    The input does not need to be a complete address.
    :param input_address: Any string
    :return: returns the stargate address as a list if validation is okay and False if not.
    """
    from ast import literal_eval
    # If the input is not a string or a list
    if not isinstance(input_address, (str, list)):
        print(f'ERROR: {input_address} must be str or list!')
        print(f'type is {type(input_address)}')
        return False
    # Make sure we are working with a list type
    address = None #initialize the variable
    if type(input_address) == str:
        try:
            if type(literal_eval(input_address)) == list:
                address = literal_eval(input_address)
        except:
            print(f'Unable to convert {input_address} to list')
            return False
    else:
        address = input_address # If it's already a list

    # Check if the list only contains integers.
    try:
        if all(isinstance(x, int) for x in address):
            return address
    except:
        return False
    return False
def all_chevrons_off(chevrons, sound=None):
    """
    A helper method to turn off all the chevrons
    :param sound: Set sound to 'on' if sound is desired when turning off a chevron light.
    :param chevrons: the dictionary of chevrons
    :return: Nothing is returned
    """
    for chev in chevrons:
        if sound == 'on':
            chevrons[chev].off(sound='on')
        else:
            chevrons[chev].off()
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
def audio_volume(percent_value):
    """
    Attempt to set the audio volume level according to the percent_value.
    :param percent_value: an integer between 0 and 100. 65 seems good.
    :return: Nothing is returned.
    """
    import subprocess
    try:
        subprocess.run(['amixer', '-M', 'set', 'Headphone', f'{str(percent_value)}%'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(['amixer', '-M', 'set', 'PCM', f'{str(percent_value)}%'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(['amixer', '-M', 'set', 'Speaker', f'{str(percent_value)}%'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        log('sg1.log', f'Audio set to {percent_value}%')
    except:
        log('sg1.log', 'Unable to set the volume. You can set the volume level manually by running the alsamixer command.')
def software_update(current_version):
    """
    This functions tries to update the stargate program with new files listed in the database
    main.py must always be updated due to the version variable change in the file.
    The owner and group of the files is set to match the same as the current __file__ variable.
    If the requirements.txt file is updated the missing modules will be installed.
    :return: Nothing is returned.
    """
    import pymysql, dbinfo, requests, pwd, grp, sys, subprocess
    from os import stat, makedirs, path
    from base64 import b64decode
    from ast import literal_eval
    from pathlib import Path

    ## Some needed variables
    update_found = None
    base_url = 'https://thestargateproject.com/stargate_software_updates/'
    root_path = Path(__file__).parent.absolute()
    # get the user ID and group ID of the owner of this file (__file__). (In most instances this would result in the UID 1001 for the sg1 user.
    uid = pwd.getpwnam(pwd.getpwuid(stat(__file__).st_uid).pw_name).pw_uid
    gid = grp.getgrnam(pwd.getpwuid(stat(__file__).st_uid).pw_name).gr_gid

    ### Get the information from the DB ###
    db = pymysql.connect(host=dbinfo.db_host, user=dbinfo.db_user, password=str(b64decode(dbinfo.db_pass), 'utf-8'), database=dbinfo.db_name)
    cursor = db.cursor()
    sql = f"SELECT * FROM `software_update`"
    cursor.execute(sql)
    sw_update = cursor.fetchall()
    db.close()

    ## check the db information for a new update
    for entry in sw_update:

        ## if there is a newer version:
        if entry[1] > current_version:
            update_audio = play_random_audio_clip(str(root_path / "soundfx/update/"))
            update_found = True
            print(f'Newer version {entry[1]} detected!')
            log('sg1.log', f'Newer version {entry[1]} detected!')

            new_files = literal_eval(entry[2]) # make a list of the new files
            # Get the new files
            for file in new_files:
                r = requests.get(base_url + str(entry[1]) + '/' + file, auth=('Samantha', 'CarterSG1!')) # get the file
                filepath = Path.joinpath(root_path, file) # the path of the new file
                try:
                    makedirs(path.dirname(filepath)) # create directories if they do not exist:
                except:
                    pass
                open(filepath, 'wb').write(r.content) # save the file
                os.chown(str(root_path / file), uid, gid) # Set correct owner and group for the file
                print (f'{file} is updated!')
                log('sg1.log', f'{file} is updated!')

                #If requirements.txt is new, run install of requirements.
                if file == 'requirements.txt':
                    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", Path.joinpath(root_path, 'requirements.txt')])
            # Don't cut the update audio short the update
            if update_audio.is_playing():
                update_audio.wait_done()
    if update_found:
        log('sg1.log', 'Update installed -> restarting the program')
        print('Update installed -> restarting the program')
        os.execl(sys.executable, *([sys.executable] + sys.argv))  # Restart the program
def check_internet_connection():
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
def get_usb_audio_device_card_number():
    """
    This function gets the card number for the USB audio adapter.
    :return: It will return a number (string) that should correspond to the card number for the USB adapter. If it can't find it, it returns 1
    """
    import subprocess
    audio_devices = subprocess.run(['aplay', '-l'], capture_output=True, text=True).stdout.splitlines()
    for line in audio_devices:
        if 'USB' in line:
            return line[5]
    return 1
def get_active_audio_card_number():
    """
    This function gets the active audio card number from the /usr/share/alsa/alsa.conf file.
    :return: It will return an integer that should correspond to the card number for the USB adapter. If it can't find it, it returns 1
    """
    # Get the contents of the file
    with open('/usr/share/alsa/alsa.conf') as alsa_file:
        lines = alsa_file.readlines()
    for line in lines:
        if 'defaults.ctl.card ' in line:
            return line[-2]
def set_correct_audio_output_device():
    """
    This functions checks if the USB audio adapter is correctly set in the alsa.conf file and fixes it if not.
    :return: Nothing is returned
    """
    import subprocess
    # If the wrong card is set in the alsa.conf file
    if get_usb_audio_device_card_number() != get_active_audio_card_number():
        log('sg1.log', f'Updating the alsa.conf file with card {get_usb_audio_device_card_number()}')
        print(f'Updating the alsa.conf file with card {get_usb_audio_device_card_number()}')

        ctl = 'defaults.ctl.card ' + str(get_usb_audio_device_card_number())
        pcm = 'defaults.pcm.card ' + str(get_usb_audio_device_card_number())
        # replace the lines in the alsa.conf file.
        subprocess.run(['sudo', 'sed', '-i', f"/defaults.ctl.card /c\{ctl}", '/usr/share/alsa/alsa.conf'])
        subprocess.run(['sudo', 'sed', '-i', f"/defaults.pcm.card /c\{pcm}", '/usr/share/alsa/alsa.conf'])
def get_DHD_port():
    """
    This is a simple helper function to help locate the port for the DHD
    :return: The file path for the DHD is returned. If it is not found, returns None.
    """
    # A list for places to check for the DHD
    possible_files = ["/dev/serial/by-id/usb-Adafruit_ItsyBitsy_32u4_5V_16MHz_HIDPC-if00", "/dev/ttyACM0", "/dev/ttyACM1"]

    # Run through the list and check if the file exists.
    for file in possible_files:
        # If the file exists, return the path and end the function.
        if os.path.exists(file):
            return file

    # If the DHD is not detected
    return None
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