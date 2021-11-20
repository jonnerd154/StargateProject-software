from HardwareDetector import HardwareDetector

# You can change or the values in this file to match your setup. This file should not be overwritten with an automatic update
# The first number in the parenthesis is the gpio led number and the second value is the motor number.

class ChevronManager:

    def __init__(self, app):

        self.log = app.log
        self.cfg = app.cfg
        
       
        self.loadFromConfig()
        
    def loadFromConfig(self):
        # Detect the connected Motor Hardware
        hwDetector = HardwareDetector()
        self.motorHardwareMode = hwDetector.getMotorHardwareMode()

        # Retrieve the Chevron config and initialize the Chevron objects
        self.chevrons = {}
        for key, value in self.cfg.get("chevronMapping").items():
            self.chevrons[int(key)] = Chevron(value['ledPin'], value['motorNumber'], self.motorHardwareMode)
            
    def get( self, chevronNumber ):
        return self.chevrons[int(chevronNumber)]
    
    def all_off(self, sound=None):
        """
        A helper method to turn off all the chevrons
        :param sound: Set sound to 'on' if sound is desired when turning off a chevron light.
        :param chevrons: the dictionary of chevrons
        :return: Nothing is returned
        """
        for number, chevron in self.chevrons.items():
            if sound == 'on':
                chevron.off(sound='on')
            else:
                chevron.off()


class Chevron:
    """
    This is the class to create and control Chevron objects.
    The led_gpio variable is the number for the gpio pin where the led-wire is connected as an int.
    The motor_number is the number for the motor as an int.
    """
    from time import sleep
    def __init__(self, led_gpio, motor_number, motorHardwareMode):
        from pathlib import Path
        from gpiozero import LED
        import simpleaudio as sound
        # If we provide a LED gpio number
        if led_gpio is not None:
            self.led = LED(led_gpio)
        else:
            self.led = None
            
        self.motor_number = motor_number
        self.root_path = Path(__file__).parent.absolute()

        ### Make ready the sound effects ###
        self.chev1 = sound.WaveObject.from_wave_file(str(self.root_path / "../soundfx/chev_usual_1.wav"))
        self.chev2 = sound.WaveObject.from_wave_file(str(self.root_path / "../soundfx/chev_usual_2.wav"))
        self.chev3 = sound.WaveObject.from_wave_file(str(self.root_path / "../soundfx/chev_usual_3.wav"))

        ### Make ready the sound effects for incoming wormhole ###
        self.chev4 = sound.WaveObject.from_wave_file(str(self.root_path / "../soundfx/chev_usual_4.wav"))
        self.chev5 = sound.WaveObject.from_wave_file(str(self.root_path / "../soundfx/chev_usual_5.wav"))
        self.chev6 = sound.WaveObject.from_wave_file(str(self.root_path / "../soundfx/chev_usual_6.wav"))
        self.chev7 = sound.WaveObject.from_wave_file(str(self.root_path / "../soundfx/chev_usual_7.wav"))
        self.possible_incoming_sounds = [self.chev4, self.chev5, self.chev6, self.chev7]

        self.enableMotors = False # TODO: Move to cfg
        self.motorHardwareMode = motorHardwareMode
        self.motor = self.get_motor_controller()

    def get_adafruit_chevron_config(self):
        # TODO: Move this out to a module that represents all of the hardware, so it can be switched out.
        from adafruit_motorkit import MotorKit
        # return {
#             1: MotorKit().motor1,
#             2: MotorKit().motor2,
#             3: MotorKit().motor3,
#             4: MotorKit().motor4,
#             5: MotorKit(address=0x61).motor1,
#             6: MotorKit(address=0x61).motor2,
#             7: MotorKit(address=0x61).motor3,
#             8: MotorKit(address=0x61).motor4,
#             9: MotorKit(address=0x62).motor1,
#             10: MotorKit(address=0x62).motor2,
#             11: MotorKit(address=0x62).motor3,
#             12: MotorKit(address=0x62).motor4
#         }
        
    def get_adafruit_motor(self, motor_number):
        # TODO: Move this out to a module that represents all of the hardware, so it can be switched out.
        #return self.get_adafruit_chevron_config()[motor_number]
        from adafruit_motorkit import MotorKit
        
        if motor_number == 1:
            motor = MotorKit().motor1
        elif motor_number == 2:
            motor = MotorKit().motor2
        elif motor_number == 3:
            motor = MotorKit().motor3
        elif motor_number == 4:
            motor = MotorKit().motor4
        elif motor_number == 5:
            motor = MotorKit(address=0x61).motor1
        elif motor_number == 6:
            motor = MotorKit(address=0x61).motor2
        elif motor_number == 7:
            motor = MotorKit(address=0x61).motor3
        elif motor_number == 8:
            motor = MotorKit(address=0x61).motor4
        elif motor_number == 9:
            motor = MotorKit(address=0x62).motor1
        elif motor_number == 10:
            motor = MotorKit(address=0x62).motor2
        elif motor_number == 11:
            motor = MotorKit(address=0x62).motor3
        elif motor_number == 12:
            motor = MotorKit(address=0x62).motor4
        else:
            motor = None
        
        return motor
        
    def get_motor_controller(self):
        # If we have motor drivers, and they are enabled in config, initialize it.
        if self.enableMotors and self.motorHardwareMode > 0:
            if self.motorHardwareMode == 1:
                return self.get_adafruit_motor(self.motor_number)
            
            ### put other motor driver options here
                        
            else:
                from hardware_simulation import DCMotorSim
                return DCMotorSim()
        else:
        	from hardware_simulation import DCMotorSim
        	return DCMotorSim()
        	
    def on(self):
        from adafruit_motorkit import MotorKit
        
        ### Chevron Down ###
        self.chev1.play() # chev down audio
        self.sleep(0.2)

        self.motor.throttle = -0.65
        self.sleep(0.1) # Motor movement time
        self.motor.throttle = None

        ### Turn on the LED ###
        self.sleep(0.35) # wait time without motion
        self.chev3.play() # led on audio
        if self.led:
            self.led.on()
        self.sleep(0.35) # wait time without motion

        ### Chevron Up ###
        self.chev2.play() # chev up audio
        self.motor.throttle = 0.65
        self.sleep(0.2) # motor movement time
        self.motor.throttle = None

    def incoming_on(self):
        from random import choice
        if self.led:
            self.led.on()
        choice(self.possible_incoming_sounds).play().wait_done()  # random led on audio

    def off(self, sound=None):
        from random import choice
        if sound == 'on':
            choice(self.possible_incoming_sounds).play()  # random led on audio
        if self.led:
            self.led.off()
