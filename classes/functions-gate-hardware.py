def all_chevrons_off(chevrons, sound=None):
    """
    A helper method to turn off all the chevrons
    :param sound: Set sound to 'on' if sound is desired when turning off a chevron light.
    :param chevrons: the dictionary of chevrons
    :return: Nothing is returned
    """
    for chev in chevrons:
        if sound == 'on':
            chevrons[chev].off(sound='on')
        else:
            chevrons[chev].off()
