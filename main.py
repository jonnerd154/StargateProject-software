"""
This is the stargate program for running the stargate from https://thestargateproject.com
This main.py file is run automatically on boot. It is executed in the .bashrc file for the sg1 user.
"""
from helper_functions import log, software_update, check_internet_connection, set_correct_audio_output_device

version = 3.7 # The current Program version as type float.
# New in version 3.5: Fix an issue with audio output. The program will now edit the alsa.conf file to set the USB audio adapter as output.
# New in version 3.6: DHD detection update. Planet/stargate name is used in the log instead of the IP.
# New in version 3.7: The Stargate server will now also start with eth0 interface only. (If subspace or wlan is missing)

### Self update feature ###
if check_internet_connection():
    try:
        software_update(version)
    except Exception as ex:
        print(ex)
        log('sg1.log', f'Software update failed with error: {ex}')

### Check/set the correct USB audio adapter. This is necessary because different raspberries detects the USB audio adapter differently.
try:
    set_correct_audio_output_device()
except:
    pass

### Boot up the Stargate ###
from classes.STARGATE_SG1 import StargateSG1

#Create the Stargate object
log('sg1.log', f'Booting up the Stargate! Version {version}')
print (f'Booting up the Stargate! Version {version}')
stargate = StargateSG1()

# Keep the script running and monitor for updates with the update() method.
stargate.update() #This will keep running as long as stargate.running is True.

# Release the ring when exiting. Just in case.
stargate.ring.release()

# Exit
print('Exiting')
log('sg1.log', 'The Stargate program is no longer running')