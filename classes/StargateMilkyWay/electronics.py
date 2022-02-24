from hardware_detection import HardwareDetector

class Electronics: # pylint: disable=too-few-public-methods

    def __new__(self, app):
        # Detect Hardware
        hw_mode = HardwareDetector(app).get_motor_hardware_mode()

        # initialize the correct subclass
        if hw_mode > 0:
            if hw_mode == HARDWARE_MODE_ORIGINAL:
                from electronics_original import ElectronicsOriginal # pylint: disable=import-outside-toplevel
                return ElectronicsOriginal(app)
        else:
            from electronics_none import ElectronicsNone # pylint: disable=import-outside-toplevel
            return ElectronicsNone()
