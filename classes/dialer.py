from time import sleep
from dial_home_devices import DHDv2, KeyboardMode

class Dialer:

    def __init__(self, log):

		# TODO: Move to config
		self.DHD_port = "/dev/serial/by-id/usb-Adafruit_ItsyBitsy_32u4_5V_16MHz_HIDPC-if00"
		self.DHD_baud_rate = 115200

		self.dialerHardware = None
		self.log = log

	def _connect_dialer(self):
		# Detect if we have a DHD connected, else use the keyboard
		try:
			self.dialerHardware = self.connect_dhd()
		except:
			self.log.log('No DHD found, switching to keyboard mode')
			self.dialerHardware = KeyboardMode()

	def _connect_dhd(self):
		### Connect to the DHD object. Will throw exception if not present
		dhd = DHDv2(self.DHD_port, self.DHD_baud_rate)
		self.log.log('DHDv2 Found. Connected.')

		dhd.setBrightnessCenter(100)
		dhd.setBrightnessSymbols(3)

		# Blink the middle button to signal the DHD is ready
		dhd.setPixel(0, 255, 255, 255)
		dhd.latch()
		sleep(0.5)
		dhd.setAllPixelsToColor(0, 0, 0)
		dhd.latch()

		return dhd
