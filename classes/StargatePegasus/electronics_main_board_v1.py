class ElectronicsMainBoard:

    def __init__(self, app):

        self.cfg = app.cfg

        self.name = "Stargate Pegasus Main Board"

        self.stepper_motor_enable = self.cfg.get("stepper_motor_enable")
        self.led_driver_address = 0x40

    # ------------------------------------------
