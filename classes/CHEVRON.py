class Chevron:
    """
    This is the class to create and control Chevron objects.
    The led_gpio variable is the number for the gpio pin where the led-wire is connected as an int.
    The motor_number is the number for the motor as an int.
    """
    from time import sleep
    def __init__(self, led_gpio, motor_number):
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


    def on(self):
        from adafruit_motorkit import MotorKit

       ### determine the right motor for the chevron ###
        if self.motor_number == 1:
            motor = MotorKit().motor1
        elif self.motor_number == 2:
            motor = MotorKit().motor2
        elif self.motor_number == 3:
            motor = MotorKit().motor3
        elif self.motor_number == 4:
            motor = MotorKit().motor4
        elif self.motor_number == 5:
            motor = MotorKit(address=0x61).motor1
        elif self.motor_number == 6:
            motor = MotorKit(address=0x61).motor2
        elif self.motor_number == 7:
            motor = MotorKit(address=0x61).motor3
        elif self.motor_number == 8:
            motor = MotorKit(address=0x61).motor4
        elif self.motor_number == 9:
            motor = MotorKit(address=0x62).motor1
        elif self.motor_number == 10:
            motor = MotorKit(address=0x62).motor2
        elif self.motor_number == 11:
            motor = MotorKit(address=0x62).motor3
        elif self.motor_number == 12:
            motor = MotorKit(address=0x62).motor4
        else:
            motor = None

        ### Chevron Down ###
        self.chev1.play() # chev down audio
        self.sleep(0.2)

        motor.throttle = -0.65
        self.sleep(0.1) # Motor movement time
        motor.throttle = None

        ### Turn on the LED ###
        self.sleep(0.35) # wait time without motion
        self.chev3.play() # led on audio
        if self.led:
            self.led.on()
        self.sleep(0.35) # wait time without motion

        ### Chevron Up ###
        self.chev2.play() # chev up audio
        motor.throttle = 0.65
        self.sleep(0.2) # motor movement time
        motor.throttle = None

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