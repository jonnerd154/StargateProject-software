import ast
from datetime import datetime

from database import Database
from stargate_address_book import StargateAddressBook

class StargateAddressManager:

    def __init__(self, stargate):

        self.stargate = stargate
        self.log = stargate.log
        self.cfg = stargate.cfg
        self.netTools = stargate.netTools
        self.base_path = stargate.base_path

        self.database = Database(stargate.base_path)
        self.addressBook = StargateAddressBook(self)

        # TODO: Refactor code to use the address book, rather than these variables
        self.known_planets = self.addressBook.get_standard_gates()

        ### Retrieve and merge all fan gates, local and in-DB
        self.fan_gates = self.addressBook.get_fan_gates() ### Stargate fan-made gate addresses

        self.validator = StargateAddressValidator()

        # Update the fan gates from the DB every x minutes
        interval = self.cfg.get("fan_gate_refresh_interval")
        stargate.app.schedule.every(interval).minutes.do( self.update_fan_gates_from_db )

    def getBook(self):
        return self.addressBook

    def is_valid(self, address):
        return self.validator.is_valid(address)

    def get_planet_name_by_address(self, address):
        # Get only the first 6 symbols
        address_compare = address[0:6]

        entry = self.addressBook.get_entry_by_address(address_compare)
        if (entry):
            return entry['name']

        # TODO: Compare to Fan Gates and Local Gates, too!
        return "Unknown Address"

    def get_fan_gates(self):
        #TODO: Remove
        return self.addressBook.get_fan_gates()

    def update_fan_gates_from_db(self):
        """
        This function gets the fan_gates from the database and merges it with the hard_coded fan_gates dictionary
        :param hard_coded_fan_gates_dictionary: The dictionary containing any hard coded fan_gates not in the database, or a local gate perhaps
        :return: The updated fan_gate dictionary is returned.
        """
        self.log.log("Updating Fan Gates from Database")
        if self.stargate.netTools.has_internet_access():
            for gate in self.database.get_fan_gates():
                # Setup the variables
                name = gate[0]
                gate_address = ast.literal_eval(gate[1])
                ip_address = self.netTools.get_ip(gate[2])

                # Add it to the datastore
                self.addressBook.set_fan_gate(name, gate_address, ip_address)

            self.cfg.set('last_fan_gate_update', str(datetime.now()))
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
        return self.addressBook.get_entry_by_address(copy_of_address)

    def is_black_hole(self, address):
        # Helper function for abstraction
        if ( self.addressBook.is_black_hole_by_address(address)):
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
        local_address = self.addressBook.get_local_address()
        for gate in self.get_fan_gates():
            try:
                #If we dial our own local address:
                if dialed_address[:2] == local_address[:2]: # TODO: This should be handled by self.valid_planet(), remove.
                    return False
                # If we dial a known fan_gate
                #TODO: Use addressBook
                elif dialed_address[:2] == self.fan_gates[gate]['gate_address'][:2]:
                    return True
            except:
                pass
        return False

    def verify_address_available(self, address):
        if len(address) < 6:
            return False, "Address requires 6 symbols", None

        remove_dups = list(dict.fromkeys(address))
        if len(remove_dups) < 6:
            return False, "Each symbol can only be used once.", None

        entry = self.addressBook.get_entry_by_address(address)
        if entry:
            if entry['type'] == "standard":
                return False, "This address is already in use by {}".format(entry['name']), entry
            if entry['type'] == "fan":
                return "VERIFY_OWNED", "Address in use by a fan gate.", entry

        return True, "", None


class StargateAddressValidator:

    def __init__(self):
        pass

    def is_valid(self, input_address): # was called validate_string_as_stargate_address
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
