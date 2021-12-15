from time import sleep

class StepperSim:

    def __init__(self):

        self.onestepTime = 0#0.0038 # in seconds, how long does a step take to exec on real HW
        pass

    def onestep(self, direction, style):
        sleep(self.onestepTime)
        pass

    def release(self):
        pass

class DCMotorSim:

    def __init__(self):
        self.throttle = 0
        pass

    def onestep(self, direction, style):
        pass

    def release(self):
        pass


class LEDSim:
    def __init__(self):
        pass

    def on(self):
        pass

    def off(self):
        pass

class NeopixelSim:

	def __init__(self):
		pass

	def show(self):
		pass

	def fill(self, color_tuple):
		pass

	def __setitem__(self, index, val):
		return None

	def __getitem__(self, index):
		return [ [], [], [] ]
