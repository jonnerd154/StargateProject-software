import os
import subprocess

class Temperature:

    def __init__(self, log):
        self.log = log

    @staticmethod
    def get_temperature():
        """
        A little helper that returns the output of the temperature command
        By default the command is available on Raspberry Pi OS (Lite)
        Command: `vcgencmd measure_temp | cut -d "=" -f2`

        :return: returns the output as seen if run in a shell.
        """
        try:
            result = subprocess.run(
                'vcgencmd measure_temp | cut -d "=" -f2',
                shell=True,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            return f"Error getting temperature: {e}"
