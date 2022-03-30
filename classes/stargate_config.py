import sys
import json
import shutil
import os
import collections
import ipaddress
from dateutil.parser import parse as parse_date

sys.path.append('config')

class StargateConfig:

    def __init__(self, base_path, file_name, galaxy_path):

        self.file_name = file_name
        self.conf_dir = base_path + "/config" #No trailing slash
        self.log = None # call set_log when log is available
        self.galaxy_path = galaxy_path

        self.config = None
        self.config_defaults = None

        # pass now, setup the logger, then set the logger, then use the class

    def load(self):
        # Open the json file and load it into a python object
        try:
            #print(f"Loading {self.file_name}")
            with open(self.get_full_file_path(), "r", encoding="utf8") as file:
                self.config = json.load(file)
            self.load_defaults() # load the defaults in case we need them later
        except FileNotFoundError:
            # The Config file doesn't exist
            # Check if there's a default config available to load
            self.copy_default_config_file()
            self.log.log(f"*** Configuration initialized with default file {self.file_name}")

    def load_defaults(self):
        # Open the json file and load it into a python object
        try:
            with open(self.get_default_file_path(), "r", encoding="utf8") as file:
                self.config_defaults = json.load(file)
        except FileNotFoundError:
            # The Config file doesn't exist
            self.log.log(f"Default Configuration for {self.file_name} not found!")

    def get_default_file_path(self):
        return self.conf_dir + "/defaults-" + self.galaxy_path + "/" + self.file_name + ".json.dist"

    def copy_default_config_file(self):
        # If the file exists, copy the file into the config directory
        try:
            shutil.copyfile( self.get_default_file_path(), self.get_full_file_path())
            os.chmod(self.get_full_file_path(), 0o655)
        except FileNotFoundError:
            print(f"Default Configuration file not found for {self.file_name}. Quitting.")
            sys.exit(1)
            return

        # Call load() so we can use the newly loaded config
        self.load()

    def set_log(self, log):
        self.log = log

    def get_full_file_path(self):
        return self.conf_dir + "/" + self.galaxy_path + "-" + self.file_name + ".json"

    def get(self, key):
        config = self.get_full_config_by_key( key )
        ret_val = []
        if config['type'] == "list-with-meta":
            for nested_attr in config['value'].values():
                ret_val.append(nested_attr['value'])
            return ret_val
        return config['value']

    def get_full_config_by_key(self, key):
        try:
            config_record = self.config.get(key)

            if config_record is None:
                raise TypeError(f"Config key {key} not found in local config")

        except (TypeError, json.decoder.JSONDecodeError) as ex:
            # Check if the key is found in the defaults.
            try:
                config_record = self.config_defaults.get(key)
                # We found the config key in the defaults, copy it to the local config
                self.log.log(f"Setting new config value from defaults {key}")
                self.__set_direct(key, config_record)

            except json.decoder.JSONDecodeError as ex:
                self.log.log(f"Key {key} not found in defaults.")
                raise TypeError(f"Config key {key} not found in defaults") from ex
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

        except TypeError as ex:
            # We should never hit this case in production.
            self.log.log(f"!!!!!!! config key {key} is missing metadata")
            raise TypeError(f"Config key {key} not found in default or local config") from ex


        return config_record

    def get_all_configs(self):
        return self.config

    def set_bulk(self, data):
        '''
        Accepts a dict containing configurations to update.
        Validates all inputs, raises ValueError on invalid input values
        Returns: dict of values updated, with new values.
        '''
        data_out = {}
        for attr_key, attr_value in data.items():
            # Validate all of the inputs before modifying anything
            try:
                attr_value = self.is_valid_value(attr_key, attr_value) # raises ValueError if not valid
                self.log.log(f"Web Config:: {attr_key} = {attr_value}")
                data_out[attr_key] = attr_value
            except ValueUnchanged: # It's okay if the value wasn't changed
                pass

        # We get here if there were no validation problems. Update the CHANGED values
        self.__set_raw_bulk(data_out)
        return data_out

    def __set_raw_bulk(self, data):
        '''
        Without validation, sets and persists a dictionary of key/value pairs
        '''
        for attr_key, attr_value in data.items():
            self.__set_raw( attr_key, attr_value )

    def __set_raw(self, key, value):
        '''
        Without validation, sets and persists a single key/value pair
        '''
        self.set_non_persistent(key, value)
        self.save()

    def __set_direct(self, key, configuration):
        '''
        Without validation, sets and persists a complete configuration element
        '''
        self.config[key] = configuration
        self.save()

    def set(self, key, value):
        '''
        Validates, sets, and persists the key/value pair.
        If the input is invalid, ValueError is raised.
        '''
        try:
            value = self.is_valid_value(key, value) # raises ValueError if not valid
        except ValueUnchanged:
            pass # It's okay if the value wasn't changed

        # If we get here without exception, the value is valid and ready to store.
        self.__set_raw(key, value) # Sets and saves new value.

    def is_valid_value( self, key, test_value ):
        '''
        Validates a configuration key/value pair
        Returns: validated/typed value
        Raises:
            - NameError (Key not found in store)
            - ValueUnchanged (passed test_value is the same as stored value)
            - ValueError (Value failed type-specific validation)
        '''
        # Check if this key exists, if not, raise NameError
        try:
            param_config = self.get_full_config_by_key(key)
            required_type = param_config['type'].lower()
            try:
                nullable = param_config['nullable']
            except KeyError:
                nullable = False

        except (TypeError, json.decoder.JSONDecodeError) as ex:
            raise TypeError(f"Config key {key} not found") from ex

        if required_type == "bool":
            if not isinstance(test_value, bool ):
                if test_value.lower() == "true":
                    test_value = True
                elif test_value.lower() == "false":
                    test_value = False
                else:
                    raise ValueError(f"{key} must be type `bool`")

        elif required_type == "str":
            if not isinstance(test_value, str ):
                raise ValueError(f"{key} must be type `str`")

        elif required_type == "str-datetime":
            if not isinstance(test_value, str ):
                raise ValueError(f"{key} must be type `str`")
            if not self.is_valid_datetime(test_value):
                raise ValueError(f"{key} requires a valid datetime")

        elif required_type == "str-enum":
            if not isinstance(test_value, str ):
                raise ValueError(f"{key} must be type `str`")
            if test_value not in param_config['enum_values']:
                raise ValueError(f"{key} must be one of {param_config['enum_values']}" )

        elif required_type == "str-ip":
            if not isinstance(test_value, str ):
                raise ValueError(f"{key} must be type `str`")
            if test_value != "" and not self.is_valid_ip_address(test_value): # Allow blanks
                raise ValueError(f"{key} must be a valid IP Address")

        elif required_type == "float":
            try:
                test_value = float(test_value)
            except ValueError as ex:
                # if the float can be an int without loss of precision, that's okay
                if test_value == float(test_value):
                    test_value = float(test_value)
                else:
                    raise ValueError(f"{key} must be type `float`") from ex

            if param_config['max_value'] and test_value > param_config['max_value']:
                raise ValueError(f"{key} Maximum value: {param_config['max_value']}")
            if param_config['max_value'] and test_value < param_config['min_value']:
                raise ValueError(f"{key} Minimum value: {param_config['min_value']}")

        elif required_type == "int":
            if test_value == "" and nullable:
                pass
            else:
                try:
                    test_value = int(test_value)
                except ValueError as ex:
                    raise ValueError(f"{key} must be type `int` got {test_value}") from ex

                if param_config['max_value'] and test_value > param_config['max_value']:
                    raise ValueError(f"{key} Maximum value: {param_config['max_value']}")
                if param_config['max_value'] and test_value < param_config['min_value']:
                    raise ValueError(f"{key} Minimum value: {param_config['min_value']}")


        elif required_type == "dict":
            if not isinstance(test_value, dict ):
                raise ValueError(f"{key} must be type `dict`")

        else:
            test_type = test_value.__class__.__name__
            raise ValueError(f"Unknown record type. {key} requires {required_type} received {test_type}")

        # Double check that our transformations yielded the correct type
        base_type = required_type.split("-", 1)[0]
        test_type = test_value.__class__.__name__
        if not nullable and test_type != base_type:
            raise ValueError(f"Validation yielded invalid type for field {key}. Requires {base_type}, yielded {test_type}")

        if nullable and test_value == "":
            test_value = None

        # Check if the existing value is the same as the test_value. If so, raise ValueUnchanged
        if test_value == param_config['value']:
            raise ValueUnchanged()

        return test_value

    @staticmethod
    def is_valid_ip_address(address):
        try:
            ipaddress.ip_address(address)
            return True
        except ValueError:
            return False

    @staticmethod
    def is_valid_datetime( value ):
        try:
            parse_date(value)
            return True
        except ValueError:
            return False

    def set_non_persistent(self, key, value):
        self.config[key]['value'] = value

    def save(self, sort=False):
        if sort:
            self.config = collections.OrderedDict(sorted(self.config.items()))

        with open(self.get_full_file_path(), 'w+', encoding="utf8") as file:
            json.dump(self.config, file, indent=2)

    def remove_all(self):
        self.config = {}
        self.save()

class ValueUnchanged(Exception):
    pass
