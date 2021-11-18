def get_DHD_port():
    """
    This is a simple helper function to help locate the port for the DHD
    :return: The file path for the DHD is returned. If it is not found, returns None.
    """
    # A list for places to check for the DHD
    possible_files = ["/dev/serial/by-id/usb-Adafruit_ItsyBitsy_32u4_5V_16MHz_HIDPC-if00", "/dev/ttyACM0", "/dev/ttyACM1"]

    # Run through the list and check if the file exists.
    for file in possible_files:
        # If the file exists, return the path and end the function.
        if os.path.exists(file):
            return file

    # If the DHD is not detected
    return None
	
