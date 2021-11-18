import spidev

class SymbolRingHomingManager:

    def __init__(self, stargate):

        self.log = stargate.log
        self.cfg = stargate.cfg
        self.audio = stargate.audio
        
        self.offset = 0
        self.homing_sensor_sensitivity = 0.15 #This is the voltage level for when the ring is in the home position.
        
        # Variables to configure the SPI and ADC peripheral hardware
        self.spi = None
        self.spi_ch = 0
        self.adc_resolution = 10 # The MCP3002 is a 10-bit ADC
        self.vref = 3.3
        
        self.ring = None

    def set_ring(self, ring):
        self.ring = ring
        
    def find_home(self):
        self.audio.sound_start('rolling_ring')  # play the audio movement
        for i in range(steps):
            if (self.motorHardwareMode > 0):
                stepper_micro_pos = stepper.onestep(direction=self.direction, style=stp.DOUBLE) + 8 # this line moves the motor.
            else:
                try:
                    stepper_micro_pos = stepper_micro_pos + 8
                except:
                    stepper_micro_pos = 8
            self.stepper_pos = (stepper_micro_pos // self.micro_steps) % self.total_steps # Update the self.stepper_pos value as the ring moves. Will have a value from 0 till self.total_steps = 1250.

            ## homing sensor ##
            try:
                if 0.000 < self.get_adc_voltage_by_channel(1) < 1: # If the jumper for the sensor is present
                    if self.get_adc_voltage_by_channel(0) < self.homing_sensor_sensitivity:  # if the ring is in the "home position"
                        # print('HOME detected!')
                        actual_position = (self.stepper_pos + self.saved_pos) % self.total_steps
                        self.offset = (self.find_offset(actual_position, self.total_steps))
            except:
                pass

            ## acceleration
            if i < acceleration_length:
                current_speed -= (slow_speed - normal_speed) / acceleration_length
                sleep(current_speed)
            ## de acceleration
            elif i > (steps - acceleration_length):
                current_speed += (slow_speed - normal_speed) / acceleration_length
                sleep(current_speed)
            ## slow without acceleration when short distance
            elif steps < acceleration_length:
                current_speed = normal_speed
                sleep(current_speed)
        self.audio.sound_stop('rolling_ring')  # stop the audio
      
    def init_spi_for_adc():  
        # Initialize the SPI hardware to talk to the external ADC
    
        # Make sure you've enabled the Raspi's SPI peripheral: `sudo raspi-config`
        self.spi = spidev.SpiDev(0, self.spi_ch)
        self.spi.max_speed_hz = 1200000
    
    def get_adc_voltage_by_channel(adc_ch):
        # CREDIT: https://learn.sparkfun.com/tutorials/python-programming-tutorial-getting-started-with-the-raspberry-pi/experiment-3-spi-and-analog-input

        self.init_spi_for_adc()
        
        # Make sure ADC channel is 0 or 1
        if adc_ch not in [0,1]:
            raise ValueError

        # Construct SPI message
        msg = 0b11 # Start bit
        msg = ((msg << 1) + adc_ch) << 5 # Select channel, read in non-differential mode
        msg = [msg, 0b00000000] # clock the response back from ADC, 12 bits
        reply = spi.xfer2(msg) # read the response and store it in a variable

        # Construct single integer out of the reply (2 bytes)
        adc_value = 0
        for byte in reply:
            adc_value = (adc_value << 8) + byte

        # Last bit (0) is not part of ADC value, shift to remove it
        adc_value = adc_value >> 1
        
        return self.adc_to_voltage(adc_value)

    def adc_to_voltage( self, adc_value):
        # Convert ADC value to voltage
        return (self.vref * adc_value) / (2^adc_resolution) #TODO: This should be minus one
