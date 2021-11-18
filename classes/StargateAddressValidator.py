
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
