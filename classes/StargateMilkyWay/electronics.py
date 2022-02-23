from hardware_detection import HardwareDetector

class Electronics: # pylint: disable=too-few-public-methods

    def __init__(self, app):
        self.app = app
        detector = HardwareDetector(app)

        self.motor_hardware_mode = detector.get_motor_hardware_mode()

        # Detect Hardware, initialize the correct subclass
        if self.motor_hardware_mode > 0:
            if self.motor_hardware_mode == 1:
                from electronics_original import ElectronicsOriginal # pylint: disable=import-outside-toplevel
                self.hardware = ElectronicsOriginal(app)
        else:
            from electronics_none import ElectronicsNone # pylint: disable=import-outside-toplevel
            self.hardware = ElectronicsNone()

        self.app.log.log(f"Detected Hardware: {self.hardware.name}")
