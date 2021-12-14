import sys
sys.path.append('config')
import json
import shutil
import sys
import os

class StargateConfig:

    def __init__(self, base_path, file_name, defaults=None):

        self.file_name = file_name
        self.confDir = base_path + "/config" #No trailing slash
        self.defaults = defaults
        self.log = None # call set_log when log is available
        
        # pass now, setup the logger, then set the logger, then use the class
        pass
       
    def load(self):
        # Open the json file and load it into a python object
        try:
            #print("Loading {}".format(self.file_name))
            f = open(self.get_full_file_path())
            self.config = json.load(f)
            f.close()
            
        except FileNotFoundError:
            # If the file wasn't found, and we were given defaults, initialize the file.
            if self.defaults is not None:
                print("*** Initializing configuration with provided defaults {}".format(self.file_name))
                self.set_defaults()
            else:
                # The Config file doesn't exist, and were weren't passed defaults.
                # Check if there's a default config available to load
                self.copy_default_config_file()
                
                
    def copy_default_config_file(self):
        # If the file exists, copy the file into the config directory
        try:
            defaults_file_path = self.confDir + "/defaults/" + self.file_name + ".dist"
            shutil.copyfile( defaults_file_path, self.get_full_file_path())
            os.chmod(self.get_full_file_path(), 0o777)
        except FileNotFoundError:
            print("Default Configuration file not found for {}. Quitting.".format(self.file_name))
            sys.exit(1)
            return
        
        print("Loaded default configuration file for {}.".format(self.file_name))
        
        # Call load() so we can use the newly loaded config
        self.load()
    
    def set_log(self, log):
        self.log = log
        
    def set_defaults(self):
        if self.defaults is not None:
            self.config = self.defaults
            self.save()
    
    def get_full_file_path(self):
        return self.confDir+"/"+self.file_name

    def get(self, key):
        try:
            return self.config.get(key)
        except json.decoder.JSONDecodeError:
            self.log.log("*** ERROR: Key '{}' not found in {}!".format(key, self.file_name))
            raise

    def set(self, key, value):
        self.set_non_persistent(key, value)
        self.save()

    def set_non_persistent(self, key, value):
        self.config[key] = value

    def save(self):   
        with open(self.get_full_file_path(), 'w+') as f:
            json.dump(self.config, f, indent=2)

    def remove_all(self):
        self.config = {}
        self.save()