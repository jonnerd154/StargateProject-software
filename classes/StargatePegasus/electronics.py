from hardware_detection import HardwareDetector

class Electronics: # pylint: disable=too-few-public-methods

    def __init__(self, app):
        self.app = app
        detector = HardwareDetector(app)

        self.hardware_mode = detector.get_hardware_mode()

        # Detect Hardware, initialize the correct subclass
        if self.hardware_mode > 0:
            if self.hardware_mode == 1:
                from electronics_main_board_v1 import ElectronicsMainBoard # pylint: disable=import-outside-toplevel
                self.hardware = ElectronicsMainBoard(app)
        else:
            from electronics_none import ElectronicsNone # pylint: disable=import-outside-toplevel
            self.hardware = ElectronicsNone(app)

        self.app.log.log(f"Detected Hardware: {self.hardware.name}")
