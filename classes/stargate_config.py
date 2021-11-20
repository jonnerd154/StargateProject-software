import sys
sys.path.append('config')
import json

class StargateConfig:

    def __init__(self, file_name, defaults=None):

        self.file_name = file_name
        self.confDir = "/home/sg1/sg1/config" #No trailing slash ## TODO: Move to config or Parent(__file__)

        # Open the json file and load it into a python object
        try:
            f = open(self.get_full_file_path())
            self.config = json.load(f)
        except:
            print("Failed to load {}.".format(self.file_name))

            # TODO: This is a fatal error, we should quit.
            raise

        if defaults is not None:
            self.config = defaults
            self.save()

    def get_full_file_path(self):
        return self.confDir+"/"+self.file_name
        
    def get(self, key):
        try:
            return self.config.get(key)
        except json.decoder.JSONDecodeError:
            print("ERROR: Key '{}' not found in {}!".format(key, self.file_name))
            raise

    def set(self, key, value):
        self.set_non_persistent(key, value)
        self.save()
    
    def set_non_persistent(self, key, value):
        self.config[key] = value

    def save(self):
        with open(self.get_full_file_path(), 'w') as f:
            json.dump(self.config, f)