
class SymbolRingHomingManager:

    def __init__(self, stargate, ring):

        self.log = stargate.log
        self.cfg = stargate.cfg
        self.audio = stargate.audio
        self.ring = ring
        self.electronics = stargate.electronics

        self.offset = 0
        self.homing_sensor_home_threshold = 0.15 #This is the voltage level for when the ring is in the home position.
        
        # Variables to configure the SPI and ADC peripheral hardware
        self.spi = None
        self.spi_ch = 0
        self.adc_resolution = 10 # The MCP3002 is a 10-bit ADC
        self.vref = 3.3
        

    def set_ring(self, ring):
        self.ring = ring
        
    def find_home(self):
        self.audio.sound_start('rolling_ring')  # play the audio movement
        for i in range(self.ring.steps):
            if (self.ring.motorHardwareMode > 0):
                stepper_micro_pos = self.ring.move_raw_one_step() + 8 # this line moves the motor.
            else:
                try:
                    stepper_micro_pos = stepper_micro_pos + 8
                except:
                    stepper_micro_pos = 8
            self.stepper_pos = (stepper_micro_pos // self.micro_steps) % self.total_steps # Update the self.stepper_pos value as the ring moves. Will have a value from 0 till self.total_steps = 1250.

            ## homing sensor ##
            try:
                homingEnabledAdc = self.electronics.get_adc_by_channel(1)
                if 0.000 < self.adc_to_voltage( homingEnabledAdc ) < 1: # If the jumper for the sensor is present
                    adc = self.electronics.get_adc_by_channel(0)
                    if self.adc_to_voltage( adc ) < self.homing_sensor_home_threshold:  # if the ring is in the "home position"
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

    def adc_to_voltage( self, adc_value):
        # Convert ADC value to voltage
        return (self.vref * adc_value) / (2^adc_resolution) #TODO: This should be minus one
