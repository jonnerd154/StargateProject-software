class HardwareDetector:

    def __init__(self, app):
        self.log = app.log
        self.hardware_mode = None
        self.signature_main_board_v1 = ['0x40'] # Mode 1
        self.hardware_mode_name = None

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

            if all( item in devices for item in self.signature_main_board_v1 ):
                self.hardware_mode_name = "Pegasus Main Board v1"
                self.hardware_mode = 1
            else:
                self.hardware_mode_name = False
                self.hardware_mode = 0

        return self.hardware_mode

    def get_hardware_mode_name(self):
        return self.hardware_mode_name
