import sys
sys.path.append('config')
import json

class StargateConfig:

    def __init__(self, file_name, defaults=None):

        self.file_name = file_name
        
        # Open the json file and load it into a python object
        try:
            f = open(file_name)
            self.config = json.load(f)
        except:
            print("Failed to load {}.".format(self.file_name))

            # TODO: This is a fatal error, we should quit.
            raise

        if defaults is not None:
            self.config = defaults
            self.save()

    def get(self, key):
        try:
            return self.config.get(key)
        except json.decoder.JSONDecodeError:
            print("ERROR: Key '{}' not found in {}!".format(key, self.file_name))
            raise

    def set(self, key, value):
        self.config[key] = value
        self.save()

    def save(self):
        with open(self.file_name, 'w') as f:
            json.dump(self.config, f)