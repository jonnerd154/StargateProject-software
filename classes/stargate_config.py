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

        self.set_defaults()

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

        self.set('enableUpdates', False)
        chevronMapping = {
            1: { 'ledPin': 6, 'motorNumber': 7 },
            2: { 'ledPin': 13, 'motorNumber': 8 },
            3: { 'ledPin': 19, 'motorNumber': 11 },
            4: { 'ledPin': 21, 'motorNumber': 3 },
            5: { 'ledPin': 16, 'motorNumber': 4 },
            6: { 'ledPin': 20, 'motorNumber': 5 },
            7: { 'ledPin': 26, 'motorNumber': 6 },
            8: { 'ledPin': None, 'motorNumber': 10 },
            9: { 'ledPin': None, 'motorNumber': 9 }
            }
        self.set('chevronMapping', chevronMapping)
