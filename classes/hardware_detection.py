
import functools

class HardwareDetector:

    def __init__(self):
        self.motorHardwareMode = None
        self.signature_adafruit_shields = ['0x60', '0x61', '0x62'] # Mode 1
        self.motorHardwareModeName = None

        self.hasSmbus = None
        self.import_smbus()

        def import_smbus():
            try:
                import smbus
                self.hasSmbus = True
                return
            except ModuleNotFoundError:
                self.hasSmbus = False
                print("Failed to import smbus. Assuming no I2C devices.")
                return


        def getI2CDevices(self):
            devices = []
            # If we don't have smbus, we have no i2c devices, return an empty array
            if not self.hasSmbus:
                return devices
            else:
                bus = smbus.SMBus(1) # 1 indicates /dev/i2c-1
                for device in range(128):
                    try:
                        bus.read_byte(device)
                        devices.append(hex(device))
                    except: # exception if read_byte fails
                        pass
                return devices

    def getMotorHardwareMode(self):
        if self.motorHardwareMode is None:
            devices = self.getI2CDevices()

            if ( all( item in devices for item in self.signature_adafruit_shields ) ):
                self.motorHardwareModeName = "Adafruit Motor Shields (3)"
                self.motorHardwareMode = 1
            else:
                self.motorHardwareModeName = False
                print("WARNING: No supported motor control hardware detected")
                self.motorHardwareMode = 0

        return self.motorHardwareMode

    def getMotorHardwareModeName(self):
        return self.motorHardwareModeName
