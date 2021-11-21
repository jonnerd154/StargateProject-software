from electronics_definitions import ElectronicsOriginal

class Electronics:

	def __init__(self, app):

		#self.log = app.log
		# self.cfg = app.cfg
		#
		# # Detect Hardware, initialize the correct subclass
		# # If we have motor drivers, and they are enabled in config, initialize it.
        # if self.enableMotors and self.motorHardwareMode > 0:
        #     if self.motorHardwareMode == 1:
		#
		# else:
        #     from hardware_simulation import DCMotorSim
        #     return DCMotorSim()

		# Return the initialized subclass

		pass

	def get_chevron_motor(self):
		pass

	def get_stepper(self):
		return self.stepper
		pass

	def get_gpio(self):
		pass
