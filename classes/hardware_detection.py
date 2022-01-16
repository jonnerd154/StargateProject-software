
import functools

class HardwareDetector:

    def __init__(self):
        self.motor_hardware_mode = None
        self.signature_adafruit_shields = ['0x60', '0x61', '0x62'] # Mode 1
        self.motor_hardware_mode_name = None

        self.smbus = False
        self.import_smbus()

    def import_smbus(self):
        try:
            import smbus  # pylint: disable=import-outside-toplevel
            self.smbus = smbus
            return
        except ModuleNotFoundError:
            self.smbus = False
            print("Failed to import smbus. Assuming no I2C devices.")
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
            except: # exception if read_byte fails
                pass
        return devices

    def get_motor_hardware_mode(self):
        if self.motor_hardware_mode is None:
            devices = self.get_i2c_devices()

            if all( item in devices for item in self.signature_adafruit_shields ):
                self.motor_hardware_mode_name = "Adafruit Motor Shields (3)"
                self.motor_hardware_mode = 1
            else:
                self.motor_hardware_mode_name = False
                print("WARNING: No supported motor control hardware detected")
                self.motor_hardware_mode = 0

        return self.motor_hardware_mode

    def get_motor_hardware_mode_name(self):
        return self.motor_hardware_mode_name
