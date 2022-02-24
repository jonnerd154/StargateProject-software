from led_driver import LEDDriver

class ElectronicsMainBoard:

    def __init__(self, app):

        self.cfg = app.cfg
        self.log = app.log

        self.name = "Stargate Pegasus Main Board"

        self.led_driver = PegasusLEDDriver( self.cfg, self.log ):

        self.gpio_pins = {}
        self.serial_to_driver = None

        self.init_gpio()

    def init_gpio(self):
        self.gpio_pins['DRIVER_BOOTSEL'] = 17
        self.gpio_pins['DRIVER_CHIPEN'] = 13
        self.gpio_pins['AUX_1'] = 24
        self.gpio_pins['ZPM_SENSE'] = 25
        self.gpio_pins['PLDC_ENABLE'] = 6
        self.gpio_pins['SHUTTER_SERVO'] = 23

        # TODO: Configure GPIO

    def init_uart_to_led_driver(self):
        self.serial_to_driver = None

        # TODO: Open UART?
