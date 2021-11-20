from time import sleep

class StepperSim:

    def __init__(self):
    
        self.onestepTime = 0.0038 # in seconds, how long does a step take to exec on real HW
        pass
        
    def onestep(self, direction, style):
        sleep(self.onestepTime)
        pass
    
    def release(self):
        pass