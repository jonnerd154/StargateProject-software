import sys
import json
import shutil
import os
from dateutil.parser import parse as parse_date

sys.path.append('config')

class StargateConfig:

    def __init__(self, base_path, file_name, defaults=None):

        self.file_name = file_name
        self.conf_dir = base_path + "/config" #No trailing slash
        self.defaults = defaults
        self.log = None # call set_log when log is available

        self.config = None

        # pass now, setup the logger, then set the logger, then use the class

    def load(self):
        # Open the json file and load it into a python object
        try:
            #print(f"Loading {self.file_name}")
            with open(self.get_full_file_path(), "r", encoding="utf8") as file:
                self.config = json.load(file)
        except FileNotFoundError:
            # If the file wasn't found, and we were given defaults, initialize the file.
            if self.defaults is not None:
                print(f"*** Initializing configuration with provided defaults {self.file_name}")
                self.set_defaults()
            else:
                # The Config file doesn't exist, and were weren't passed defaults.
                # Check if there's a default config available to load
                self.copy_default_config_file()


    def copy_default_config_file(self):
        # If the file exists, copy the file into the config directory
        try:
            defaults_file_path = self.conf_dir + "/defaults/" + self.file_name + ".dist"
            shutil.copyfile( defaults_file_path, self.get_full_file_path())
            os.chmod(self.get_full_file_path(), 0o777)
        except FileNotFoundError:
            print(f"Default Configuration file not found for {self.file_name}. Quitting.")
            sys.exit(1)
            return

        print(f"Loaded default configuration file for {self.file_name}.")

        # Call load() so we can use the newly loaded config
        self.load()

    def set_log(self, log):
        self.log = log

    def set_defaults(self):
        if self.defaults is not None:
            self.config = self.defaults
            self.save()

    def get_full_file_path(self):
        return self.conf_dir+"/"+self.file_name

    def get(self, key):
        return self.get_full_config_by_key( key )['value']

    def get_full_config_by_key(self, key):
        try:
            config_record = self.config.get(key)
        except json.decoder.JSONDecodeError:
            self.log.log(f"*** ERROR: Key '{key}' not found in {self.file_name}!")
            raise

        try:
            if config_record['type'] == 'dict':

                # Expand the values to include metadata
                for parent_key, parent_value in config_record['value'].items():
                    for config_param, param_values in parent_value.items():
                        try:
                            param_values = param_values | config_record['item_config'][config_param]
                            config_record['value'][parent_key][config_param] = param_values
                        except KeyError:
                            pass

        except ValueError:
            self.log.log(f"!!!!!!! config key {key} is missing metadata")

        return config_record

    def get_all_configs(self):
        return self.config

    def set(self, key, value):
        try:
            old = self.get_full_config_by_key(key)
        except json.decoder.JSONDecodeError:
            self.log.log("Creating config key: {key}")
            old = None

        if old is not None:
            # Check for validity
            if old['type'] != "":
                if old['type'].lower() == "boolean" and not isinstance(value, bool ):
                    raise ValueError("Must be type `bool`")

                if old['type'].lower() == "string" and not isinstance(value, str ):
                    raise ValueError("Must be type `str`")

                if old['type'].lower() == "string-datetime":
                    if not isinstance(value, str ):
                        raise ValueError("Must be type `str`")
                    if not self.is_valid_datetime(value):
                        raise ValueError("Value is not a valid datetime")

                if old['type'].lower() == "string-enum":
                    if not isinstance(value, str ):
                        raise ValueError("Must be type `str`")
                    if value not in old['enum_values']:
                        raise ValueError("Value is not one of the allowed values")

                if old['type'].lower() == "int":
                    if not isinstance(value, int ):
                        raise ValueError("Must be type `int`")
                    if old['max_value'] and value > old['max_value']:
                        raise ValueError(f"Maximum value: {old['max_value']}")
                    if old['max_value'] and value < old['min_value']:
                        raise ValueError(f"Minimum value: {old['min_value']}")

                if old['type'].lower() == "float":
                    if not isinstance(value, float ):
                        raise ValueError("Must be type `float`")
                    if old['max_value'] and value > old['max_value']:
                        raise ValueError(f"Maximum value: {old['max_value']}")
                    if old['max_value'] and value < old['min_value']:
                        raise ValueError(f"Minimum value: {old['min_value']}")
                if old['type'].lower() == "dict" and not isinstance(value, dict ):
                    raise ValueError("Must be type `dict`")

        self.set_non_persistent(key, value)
        self.save()

    @staticmethod
    def is_valid_datetime( value ):
        try:
            parse_date(value)
            return True
        except ValueError:
            return False

    def set_non_persistent(self, key, value):
        self.config[key]['value'] = value

    def save(self):
        with open(self.get_full_file_path(), 'w+', encoding="utf8") as file:
            json.dump(self.config, file, indent=2)

    def remove_all(self):
        self.config = {}
        self.save()
