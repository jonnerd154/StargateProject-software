import ast

from database import Database
from stargate_address_book import StargateAddressBook

class StargateAddressManager:

    def __init__(self, stargate):

        self.stargate = stargate
        self.log = stargate.log
        self.cfg = stargate.cfg
        self.netTools = stargate.netTools

        self.database = Database(stargate.base_path)
        self.addressBook = StargateAddressBook(self)

        # TODO: Refactor code to use the address book, rather than these variables
        self.black_hole_planets = [ known_planets["P3W-451"] ]
        
        self.local_stargate_address = self.addressBook.get_local_address() # Set the local stargate address
        self.fan_gates = self.addressBook.get_fan_gates() ### Stargate fan-made gate addresses
        self.known_planets = self.addressBook.get_standard_gates()
        
        ### Retrieve and merge all fan gates, local and in-DB
        self.fan_gates = self.update_fan_gates_from_db()

        pass

    def get_planet_name_by_address(self, address):
        # Get only the first 6 symbols
        address_compare = address[0:6]

        for key, value in known_planets.items():
            if (len(value) == len(address_compare)):
                if (value == address_compare):
                    return key
            
        # TODO: Compare to Fan Gates and Local Gates, too!
        return "Unknown Address"
        
    def get_fan_gates(self):
        return self.fan_gates

    def update_fan_gates_from_db(self):
        """
        This function gets the fan_gates from the database and merges it with the hard_coded fan_gates dictionary
        :param hard_coded_fan_gates_dictionary: The dictionary containing any hard coded fan_gates not in the database, or a local gate perhaps
        :return: The updated fan_gate dictionary is returned.
        """
        if self.stargate.netTools.has_internet_access():
            for gate in self.database.get_fan_gates():
                self.fan_gates[gate[0]] = [ast.literal_eval(gate[1]), self.netTools.get_ip(gate[2])]
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

        # You can't dial yourself
        if copy_of_address == self.local_stargate_address:
            return False

        # Check if we dialed the black hole planet
        if self.is_black_hole(copy_of_address):
            self.black_hole = True
            self.log.log("Oh no! It's the black hole planet!")

        # Check the known_planets dictionary for a match
        for planet in known_planets:
            if known_planets[planet] == copy_of_address:
                return 'known_planet'

        # Check the fan_gates dictionary for a match
        for gate in self.fan_gates:
            if self.fan_gates[gate][0] == copy_of_address:
                return 'fan_gate'
        return False  # Return False if it's not a valid destination

    def is_black_hole(self, address):
        if address in self.black_hole_planets:
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
        for gate in self.fan_gates:
            try:
                #If we dial our own local address:
                if dialed_address[:2] == self.local_stargate_address[:2]: # TODO: This should be handled by self.valid_planet(), remove.
                    return False
                # If we dial a known fan_gate
                elif dialed_address[:2] == self.fan_gates[gate][0][:2]:
                    return True
            except:
                pass
        return False

class StargateAddressValidator:

	def __init__(self, input_address):
		return self.is_valid(input_address)

	def is_valid(input_address): # was called validate_string_as_stargate_address
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
