from time import sleep
import adafruit_pixelbuf

class StepperSim:

    def __init__(self):

        self.onestep_time = 0.0038 # in seconds, how long does a step take to exec on real HW
        #self.onestep_time = 0 # For testing in "turbo sim" mode

    def onestep(self, direction, style): # pylint: disable=unused-argument
        sleep(self.onestep_time)

    def release(self):
        pass

class DCMotorSim:

    def __init__(self):
        self.throttle = 0

    def onestep(self, direction, style):
        pass

    def release(self):
        pass


class LEDSim:
    def __init__(self):
        pass

    def on(self):  # pylint: disable=invalid-name
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

    def __exit__(self, a, b, c): # pylint: disable=invalid-name
        self.deinit()

    def __repr__(self):
        return "[" + ", ".join([str(x) for x in self]) + "]"

    @property
    def n(self) -> int: # pylint: disable=invalid-name
        return len(self)

    def _transmit(self, buffer: bytearray) -> None:
        pass
