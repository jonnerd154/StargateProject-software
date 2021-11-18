#!/home/sg1/sg1_venv/bin/python3
"""
This is a script to help check if your chosen address is valid for use with your stargate. (It checks if it conflicts with other already known stargates)
This document shows what symbol has what number in this program: https://thestargateproject.com/symbols_overview.pdf
The script is designed to run from the command line as follows:
SSH into your pi and run the following command where you input your chosen address at the end as seen in this example:
/home/sg1/sg1_venv/bin/python /home/sg1/sg1/check_address.py '[7, 5, 20, 27, 32, 21]'
When you have found an address you want to use and want to add it to the public address book so other stargate builders can dial your gate,
you need to follow the instructions here: https://thestargateproject.com/address-book/#GetYourOwnAddress
"""
from helper_functions import validate_string_as_stargate_address, get_fan_gates_from_db
import sys
from hardcoded_addresses import known_planets

def usable_address(input_addr):
    """
    This functions checks the input_addr for conflicts and returns the result.
    :return: Different strings with information is returned.
    """
    if len(input_addr) < 6:
        return f'The chosen address {input_addr} is too short. You need at least 6 symbols.'
    # Check the known_planets dictionary for a conflicting address
    for planet in known_planets:
        if known_planets[planet][:2] == input_addr[:2]: # if the two first symbols clash.
            return f'Sorry, but address {input_addr} conflicts with the known_planet; {planet} -> {known_planets[planet]}'
    # Check the fan_gates dictionary for a conflicting address
    fan_gates = get_fan_gates_from_db({})
    for planet in fan_gates:
        if fan_gates[planet][0][:2] == input_addr[:2]: # if the two first symbols clash.
            return f'Sorry, but address {input_addr} conflicts with the known_planet; {planet} -> {fan_gates[planet][0]}'
    return f'CONGRATULATIONS, there are no conflicts with your chosen address; {input_addr}'

if len(sys.argv) > 2:
    print("ERROR: Too many arguments, try encapsulating the address in quotes like this example: '[7, 5, 20, 27, 32, 21]'")

address = validate_string_as_stargate_address(sys.argv[1])
if not address:
    print("ERROR: Not a valid input: Try formatting it as this example: '[7, 5, 20, 27, 32, 21]'")
else:
    print(usable_address(address))
