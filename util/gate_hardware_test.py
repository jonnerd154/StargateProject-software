"""
This is the stargate program for running the stargate from https://thestargateproject.com
This main.py file is run automatically on boot. It is executed in the .bashrc file for the sg1 user.
"""
from helper_functions import log, software_update, check_internet_connection, set_correct_audio_output_device
from time import sleep
from classes.HardwareDetector import HardwareDetector
from chevrons import chevrons
    
from adafruit_motorkit import MotorKit
from adafruit_motor import stepper as stp
import neopixel, board
        
### Check/set the correct USB audio adapter. This is necessary because different raspberries detects the USB audio adapter differently.
try:
    set_correct_audio_output_device()
except:
    pass

### Boot up the Stargate ###
#from classes.STARGATE_SG1 import StargateSG1

#Create the Stargate object
log('sg1.log', f'Test Starting')
print (f'Test Starting')
# stargate = StargateSG1()



total_steps = 1250
micro_steps = 16
stepper_pos = 0
stepper = None


# ########### WORMHOLE NEOPIXEL TESTS ###############

neoPin = board.D12  # The standard data pin is board.D18
tot_leds = 122
pixels = neopixel.NeoPixel(neoPin, tot_leds, auto_write=False, brightness=0.61)

print("Testing wormhole neopixels. Press ctrl+c to continue to next test.")
while(True):
    try:
        for i in range(20):
            pixels.fill(((i // 2) * 2, i * 2, i * 2))
            pixels.show()
        sleep(0.5)
        for i in range(20, 128):
            pixels.fill(((i // 2) * 2, i * 2, i * 2))
            pixels.show()
        for i in range(255, 50, -2):
            pixels.fill((i // 2, i, i))
            pixels.show()
        sleep(0.3)
    except KeyboardInterrupt:
        off_pattern = []
        for i in range(tot_leds):
            pixels.fill((0,0,0))
            pixels.show()
        break
    


# #### Motor Hardware Detection #################

hwDetector = HardwareDetector()
motorHardwareMode = hwDetector.getMotorHardwareMode()
modeName = hwDetector.getMotorHardwareModeName()
if (not modeName):
    print("Warning: No supported motor hardware controllers detected")
    
else:
    print("Motor Hardware FOUND: {}".format(modeName))

# ########### SYMBOL RING MOTOR TESTS ###############
# 
# if motorHardwareMode > 0:
#     stepper = MotorKit().stepper1
#     sleep(0.4)
#     stepper.release()
#     
# # move a short distance clockwise
# direct = stp.FORWARD
# speed = 0.01
# input("Moving the ring clockwise. Press enter to start.")
# while(True):
#     try:
#         for i in range(1,100):
#             stepper.onestep(direction=direct, style=stp.DOUBLE) + 8 # this line moves the motor.
#             sleep(speed)
#         sleep(0.4)
#         stepper.release()
#         inputStr = input("Press Enter to move clockwise again. Press 'n' and hit enter to move to the next test.")
#         if inputStr == "n":
#             break
#         else:
#             continue
#         
#     except KeyboardInterrupt:
#         break
# 
# direct = stp.BACKWARD
# input("Moving the ring counter-clockwise. Press enter to start.")
# while(True):
#     try:
#         for i in range(1,100):
#             stepper.onestep(direction=direct, style=stp.DOUBLE) + 8 # this line moves the motor.
#             sleep(speed)
#         stepper.release()
#         inputStr = input("Press Enter to move counterclockwise again. Press 'n' and hit enter to move to the next test.")
#         if inputStr == "n":
#             break
#         else:
#             continue
#         
#     except KeyboardInterrupt:
#         break
# 
# sleep(0.4)
# stepper.release()   
# 
# while(True):
#     direct = stp.FORWARD
#     input("CALIBRATION: The ring is unlocked. Gently move the \"Home\" symbol into the top chevron. Press enter when done.")
# 
#     # Save the current position in the file
# 
#     try:
#         for i in range(1,1250):
#             stepper.onestep(direction=direct, style=stp.DOUBLE)
#             sleep(speed)
#         stepper.release()
#         inputStr = input("Is the \"Home\" symbol at the top again? (y)es or (n)o")
#         if inputStr == "y":
#             break
#         else:
#             continue
#         
#     except KeyboardInterrupt:
#         break
# 
# while(True):
#     direct = stp.BACKWARD
# 
#     # Save the current position in the file
# 
#     try:
#         for i in range(1,1250):
#             stepper.onestep(direction=direct, style=stp.DOUBLE)
#             sleep(speed)
#         stepper.release()
#         inputStr = input("Is the \"Home\" symbol at the top again? (y)es or (n)o")
#         if inputStr == "y":
#             break
#         else:
#             continue
#         
#     except KeyboardInterrupt:
#         break
#         
# sleep(0.4)
# stepper.release()   

# ########### CHEVRON TESTS ###############

print( "Testing Chevron lights and motors. Motor should move inward, the light should turn on, then the motor should move outward. ")
for i in range(1,8):
    print("Testing Chevron {}.".format(i))
    chevrons[i].on()
    sleep(1)

# ##########################################



# Exit
print('Exiting')
log('sg1.log', 'The Stargate program is no longer running')