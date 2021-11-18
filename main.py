"""
This is the stargate program for running the stargate from https://thestargateproject.com
This main.py file is run automatically on boot. It is executed in the .bashrc file for the sg1 user.
"""
from helper_functions import log, software_update, check_internet_connection

### Self update feature ###
version = 3.3 # The current Program version as type float.
if check_internet_connection():
    try:
        software_update(version)
    except Exception as ex:
        print(ex)
        log('sg1.log', f'Software update failed with error: {ex}')

### Boot up the Stargate ###
from classes.STARGATE_SG1 import StargateSG1

#Create the Stargate object
log('sg1.log', 'Booting up the Stargate...')
stargate = StargateSG1()

# Keep the script running and monitor for updates with the update() method.
stargate.update() #This will keep running as long as stargate.running is True.

# Release the ring when exiting. Just in case.
stargate.ring.release()

# Exit
print('Exiting')
log('sg1.log', 'The Stargate program is no longer running')