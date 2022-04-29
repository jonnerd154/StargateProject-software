from ast import literal_eval
from datetime import datetime
import json
import requests

from stargate_address_book import StargateAddressBook

class StargateAddressManager:

    def __init__(self, stargate):

        self.stargate = stargate
        self.log = stargate.log
        self.cfg = stargate.cfg
        self.net_tools = stargate.net_tools
        self.base_path = stargate.base_path
        self.galaxy = stargate.galaxy
        self.galaxy_path = stargate.galaxy_path

        self.address_book = StargateAddressBook(self, self.galaxy_path)

        self.known_planets = self.address_book.get_standard_gates()

        ### Retrieve and merge all fan gates, local and in-DB
        self.fan_gates = self.address_book.get_fan_and_lan_addresses() ### Stargate fan-made gate addresses

        self.validator = StargateAddressValidator()

        self.info_api_url = self.cfg.get("subspace_public_api_url")

        # Update the fan gates from the DB every x minutes
        if self.cfg.get("fan_gate_refresh_enable"):
            update_interval = self.cfg.get("fan_gate_refresh_interval")
            stargate.app.schedule.every(update_interval).minutes.do( self.update_fan_gates_from_api )

    def get_book(self):
        return self.address_book

    def is_valid(self, address):
        return self.validator.is_valid(address)

    def get_planet_name_by_address(self, address):
        # Get only the first 6 symbols
        address_compare = address[0:6]

        entry = self.address_book.get_entry_by_address(address_compare)
        if entry:
            return entry['name']

        return "Unknown Address"

    def update_fan_gates_from_api(self):
        """
        This function gets the fan_gates from the API and stores it in the AddressBook
        :return: The updated fan_gate dictionary is returned.
        """
        self.log.log(f"Updating Fan Gates from API: {self.galaxy} Galaxy")

        if self.stargate.net_tools.has_internet_access():
            try:
                # Retrieve the data from the API
                request = requests.get(self.info_api_url + "/get_fan_gates.php?galaxy=" + self.galaxy_path, timeout=5 )
                data = json.loads(request.text)

                for gate_config in data:
                    # Setup the variables
                    name = gate_config['name']
                    gate_address = literal_eval(gate_config['sg_address'])
                    ip_address = self.net_tools.get_ip(gate_config['ip'])

                    # Add it to the datastore
                    self.address_book.set_fan_gate(name, gate_address, ip_address)

                self.log.log("Fan Gate Update: Success!")
                self.cfg.set('fan_gate_last_update', str(datetime.now()))
            except: # pylint: disable=bare-except
                self.log.log("Fan Gate Update: FAILED")

        return self.fan_gates

    def valid_planet(self, address):
        """
            A helper function to check if the dialed address is a valid planet address. This function excludes the
            last symbol in the address since the last symbol can be any point of origin.
            :param address: the destination as a list of symbol numbers
            :return:    If the dialed address is a fan_gate, the string 'fan_gate' is returned.
                        If the dialed address is a known_planet, the string 'known_planet' is returned.
                        Else: False is returned if it is not a valid planet.
            """

        # make a copy of the address, so not to manipulate the input variable directly
        copy_of_address = address[:]

        # remove the point of origin from address
        if len(copy_of_address) != 0:
            del copy_of_address[-1]

        # Look through the address book for matching addresses. Returns full book entry, or False
        return self.address_book.get_entry_by_address(copy_of_address)

    def is_black_hole(self, address):
        # Helper function for abstraction
        if self.address_book.is_black_hole_by_address(address):
            self.log.log("Oh no! It's the black hole planet!")
            return True
        return False

    def is_fan_made_stargate(self, dialed_address):
        """
        This helper function tries to check the first two symbols in the dialed address and compares it to
        the known_fan_made_stargates to check if the address dialed is a known fan made stargate. The first two symbols
        is enough to determine if it's a fan_gate. The fan gates, need only two unique symbols for identification.
        :param stargate_object: The stargate object. This is used to rule out self dialing.
        :param dialed_address: a stargate address. It does not need to be complete. eg: [10, 15, 8, 24]
        :param known_fan_made_stargates: This is a dictionary of known stargates. eg:
                {'Kristian Tysse': [[7, 32, 27, 18, 12, 16], '192.168.10.129'],
                'Someone else': [[7, 32, 27, 18, 12, 16], '1.2.3.4']
                }
        :return: True if we are dialing a fan made address, False if not.
        """
        local_address = self.address_book.get_local_address()
        for gate_config in self.address_book.get_fan_and_lan_addresses().values():
            try:
                #If we dial our own local address:
                if dialed_address[:2] == local_address[:2]:
                    return False
                # If we dial a known fan_gate
                if dialed_address[:2] == gate_config['gate_address'][:2]:
                    return True
            except (AttributeError, KeyError):
                pass
        return False

    def verify_address_available(self, address):
        if len(address) < 6:
            return False, "Address requires 6 symbols", None

        remove_dups = list(dict.fromkeys(address))
        if len(remove_dups) < 6:
            return False, "Each symbol can only be used once.", None

        entry = self.address_book.get_entry_by_address(address)
        if entry:
            if entry['type'] == "standard":
                return False, f"This address is already in use by {entry['name']}", entry
            if entry['type'] == "fan":
                return "VERIFY_OWNED", "Address in use by a fan gate.", entry

        return True, "", None

    def get_stargate_address_from_ip(self, remote_ip):
        """
        This function simply gets the stargate address that matches the IP address
        :param remote_ip: the IP address as a string
        :return: The stargate's IP address is returned as a string, or "Unknown" if not found
        """
        stargate_ip = 'Unknown'
        for stargate_config in self.address_book.get_fan_and_lan_addresses().values():
            if stargate_config['ip_address'] == remote_ip:
                return stargate_config['name'] # TODO: Should this return `gate_address`?
        return str(stargate_ip) # If the gate address of the IP was not found

    def get_ip_from_stargate_address(self, stargate_address):
        """
        This functions gets the IP address from the first two symbols in the gate_address. The first two symbols of the
        fan_gates are always unique.
        :param stargate_address: This is the destination for which to match with an IP.
        :param known_fan_made_stargates: This is the dictionary of the known stargates
        :return: The IP address is returned as a string.
        """
        for stargate_config in self.address_book.get_fan_and_lan_addresses().values():
            if len(stargate_address) > 1 and stargate_address[0:2] == stargate_config['gate_address'][0:2]:
                return stargate_config['ip_address']

        self.log.log( f'Unable to get IP for {stargate_address}')
        return None

    def get_planet_name_from_ip(self, remote_ip):
        """
        This function gets the planet name of the IP in the fan_gate dictionary.
        :param fan_gates: The dictionary of fan_gates from the API
        :param IP: the IP address as a string
        :return: The planet/stargate name is returned as a string.
        """
        for gate_name, config in self.address_book.get_fan_and_lan_addresses().items(): # pylint: disable=unused-variable
            if config['ip_address'] == str(remote_ip):
                return config['name']
        return 'Unknown'

    @staticmethod
    def get_summary_from_book( book, omit_zeros ):
        summary = {}
        summary['fan'] = 0
        summary['lan'] = 0
        summary['standard'] = 0

        for address, config in book.items(): # pylint: disable=unused-variable
            summary[config.get("type", "unknown")] +=1

        if omit_zeros:
            for name in summary.copy().keys():
                if summary[name] == 0:
                    summary.pop(name)

        return summary

class StargateAddressValidator: # pylint: disable=too-few-public-methods

    def __init__(self):
        pass

    @staticmethod
    def is_valid(input_address): # was called validate_string_as_stargate_address
        """
        This is just a simple helper function to check if the input is indeed a representation of a stargate address.
        The input does not need to be a complete address.
        :param input_address: Any string
        :return: returns the stargate address as a list if validation is okay and False if not.
        """

        # If the input is not a string or a list
        if not isinstance(input_address, (str, list)):
            print(f'ERROR: {input_address} must be str or list!')
            print(f'type is {type(input_address)}')
            return False
        # Make sure we are working with a list type
        address = None #initialize the variable
        if isinstance(input_address, str):
            try:
                if isinstance(literal_eval(input_address), list):
                    address = literal_eval(input_address)
            except AttributeError:
                print(f'Unable to convert {input_address} to list')
                return False
        else:
            address = input_address # If it's already a list

        # Check if the list only contains integers.
        try:
            if all(isinstance(x, int) for x in address):
                return address
        except AttributeError:
            return False
        return False
