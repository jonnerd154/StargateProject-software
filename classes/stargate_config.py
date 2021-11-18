import json

class StargateConfig:

    def __init__(self):

        # Open the json file and load it into a python object
        try:
            f = open('config.json')
            self.config = json.load(f)
        except:
            print("Failed to load config.json.")

            # TODO: This is a fatal error, we should quit.
            raise

        #self.set_defaults()

    def get(self, key):
        return self.config.get(key)

    def set(self, key, value):
        self.config[key] = value
        self.save()

    def save(self):
        with open('config.json', 'w') as f:
            json.dump(self.config, f)

    def set_defaults(self):
        self.config = {}

        self.set('enableUpdates', True)
