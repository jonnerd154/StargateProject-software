from adafruit_motorkit import MotorKit
from adafruit_motor import stepper as stp

class ElectronicsOriginal:

	def __init__(self):

		self.motorShield1Address = 0x60
		self.motorShield2Address = 0x61
		self.motorShield3Address = 0x62

		self.shieldConfig = None
		self.stepper = None
		self.init_motor_shields()

    def init_motor_shields(self):
		# Initialize all of the shields as DC motors
        self.shieldConfig =  {
            #1: MotorKit(address=self.motorShield1Address).motor1, # Used for Stepper
            #2: MotorKit(address=self.motorShield1Address).motor2, # Used for Stepper 
            3: MotorKit(address=self.motorShield1Address).motor3,
            4: MotorKit(address=self.motorShield1Address).motor4,
            5: MotorKit(address=self.motorShield2Address).motor1,
            6: MotorKit(address=self.motorShield2Address).motor2,
            7: MotorKit(address=self.motorShield2Address).motor3,
            8: MotorKit(address=self.motorShield2Address).motor4,
            9: MotorKit(address=self.motorShield3Address).motor1,
            10: MotorKit(address=self.motorShield3Address).motor2,
            11: MotorKit(address=self.motorShield3Address).motor3,
            12: MotorKit(address=self.motorShield3Address).motor4
        }

		# Initialize the Stepper
		self.stepper = MotorKit(address=self.motorShield1Address).stepper1

	def get_chevron_motor(self, chevron_number):
		return self.shieldConfig[chevron_number]
