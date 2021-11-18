import spidev
# Enable SPI
spi_ch = 0
spi = spidev.SpiDev(0, spi_ch)
spi.max_speed_hz = 1200000
def read_adc(adc_ch, vref=3.3):
    # CREDIT: https://learn.sparkfun.com/tutorials/python-programming-tutorial-getting-started-with-the-raspberry-pi/experiment-3-spi-and-analog-input
    # Make sure you've enabled the Raspi's SPI peripheral: `sudo raspi-config`

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

    # Calculate voltage from ADC value
    # The MCP3002 is a 10-bit ADC
    voltage = (vref * adc_value) / 1024

    return voltage