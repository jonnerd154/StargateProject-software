from time import sleep
import adafruit_pixelbuf

class StepperSim:

    def __init__(self):

        self.onestepTime = 0.0038 # in seconds, how long does a step take to exec on real HW
        #self.onestepTime = 0 # For testing in "turbo sim" mode
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

class NeopixelSim(adafruit_pixelbuf.PixelBuf):

    def __init__( self, n: int,):
        super().__init__(
            n, brightness=1.0, byteorder="GRB", auto_write=True # Can set this to False to tighten timings for testing
        )

    def deinit(self) -> None:
        self.fill(0)

    def __enter__(self):
        return self

    def __exit__(self):
        self.deinit()

    def __repr__(self):
        return "[" + ", ".join([str(x) for x in self]) + "]"

    @property
    def n(self) -> int:
        return len(self)

    def _transmit(self, buffer: bytearray) -> None:
        pass
