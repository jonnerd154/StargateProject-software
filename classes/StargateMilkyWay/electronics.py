
# Hardware Mode enums
HARDWARE_MODE_NONE = 0
HARDWARE_MODE_ORIGINAL = 1
HARDWARE_MODE_MAINBOARD_1V1 = 2

class Electronics: # pylint: disable=too-few-public-methods

    def __new__(cls, app):
        # Detect Hardware
        hw_mode = HardwareDetector(app).get_hardware_mode()

        # initialize the correct subclass
        if hw_mode > 0:
            if hw_mode == HARDWARE_MODE_ORIGINAL:
                from electronics_original import ElectronicsOriginal # pylint: disable=import-outside-toplevel
                return ElectronicsOriginal(app)
            if hw_mode == HARDWARE_MODE_MAINBOARD_1V1:
                from electronics_mainboard_1v1 import ElectronicsMainBoard1V1 # pylint: disable=import-outside-toplevel
                return ElectronicsMainBoard1V1(app)

        # Default: No Electronics, simulate everything
        from electronics_none import ElectronicsNone # pylint: disable=import-outside-toplevel
        return ElectronicsNone()


class HardwareDetector:

    def __init__(self, app):
        self.log = app.log
        self.hardware_mode = None
        self.hardware_mode_name = None

        # TODO: Refactor this to loop over the signatures in an array
        self.signature_adafruit_shields = ['0x60', '0x61', '0x62'] # HARDWARE_MODE_ORIGINAL
        self.signature_mainboard_1v1 = ['0x66', '0x6f'] # HARDWARE_MODE_MAINBOARD_1V1

        self.smbus = False
        self.import_smbus()

    def import_smbus(self):
        try:
            import smbus  # pylint: disable=import-outside-toplevel
            self.smbus = smbus
            return
        except ModuleNotFoundError:
            self.smbus = False
            self.log.log("Failed to import smbus. Assuming no I2C devices.")
            return

    def get_i2c_devices(self):
        devices = []
        # If we don't have smbus, we have no i2c devices, return an empty array
        if not self.smbus:
            return devices

        bus = self.smbus.SMBus(1) # 1 indicates /dev/i2c-1
        for device in range(128):
            try:
                bus.read_byte(device)
                devices.append(hex(device))
            except: # exception if read_byte fails # pylint: disable=bare-except
                pass
        return devices

    def get_hardware_mode(self):
        if self.hardware_mode is None:
            devices = self.get_i2c_devices()

            if all( item in devices for item in self.signature_adafruit_shields ):
                self.hardware_mode = HARDWARE_MODE_ORIGINAL
            elif all( item in devices for item in self.signature_mainboard_1v1 ):
                self.hardware_mode = HARDWARE_MODE_MAINBOARD_1V1
            else:
                self.hardware_mode = HARDWARE_MODE_NONE

        return self.hardware_mode

    def get_hardware_mode_name(self):
        return self.hardware_mode_name
