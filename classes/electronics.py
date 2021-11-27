from hardware_detection import HardwareDetector

class Electronics:

    def __init__(self, app):
        detector = HardwareDetector()

        self.motorHardwareMode = detector.getMotorHardwareMode()

        # Detect Hardware, initialize the correct subclass
        if self.motorHardwareMode > 0:
            if self.motorHardwareMode == 1:
                from electronics_original import ElectronicsOriginal
                self.hardware = ElectronicsOriginal(app)
        else:
            from electronics_none import ElectronicsNone
            self.hardware = ElectronicsNone(app)
