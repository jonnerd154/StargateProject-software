
class StargateSymbolManager:

    def __init__(self, galaxy_path):
        self.galaxy_path = galaxy_path

        self.symbols = None
        self.init_symbol_list()

    def init_symbol_list(self):
        self.symbols = [
            {
                'index': 1,
                'name': "Earth",
                'keyboard_mapping': "8"
            },
            {
                'index': 2,
                'name': "Crater",
                'keyboard_mapping': "C"
            },
            {
                'index': 3,
                'name': "Virgo",
                'keyboard_mapping': "V"
            },
            {
                'index': 4,
                'name': "Bootes",
                'keyboard_mapping': "U"
            },
            {
                'index': 5,
                'name': "Centaurus",
                'keyboard_mapping': "a"
            },
            {
                'index': 6,
                'name': "Libra",
                'keyboard_mapping': "3"
            },
            {
                'index': 7,
                'name': "Serpens Caput",
                'keyboard_mapping': "5"
            },
            {
                'index': 8,
                'name': "Norma",
                'keyboard_mapping': "S"
            },
            {
                'index': 9,
                'name': "Scorpio",
                'keyboard_mapping': "b"
            },
            {
                'index': 10,
                'name': "Cra",
                'keyboard_mapping': "K"
            },
            {
                'index': 11,
                'name': "Scutum",
                'keyboard_mapping': "X"
            },
            {
                'index': 12,
                'name': "Sagittarius",
                'keyboard_mapping': "Z"
            },
            {
                'index': 13,
                'name': "Aquila",
                'is_on_dhd': False,
                'keyboard_mapping': False
            },
            {
                'index': 14,
                'name': "Mic",
                'keyboard_mapping': "E"
            },
            {
                'index': 15,
                'name': "Capricorn",
                'keyboard_mapping': "P"
            },
            {
                'index': 16,
                'name': "Pisces Austrinus",
                'keyboard_mapping': "M"
            },
            {
                'index': 17,
                'name': "Equuleus",
                'keyboard_mapping': "D"
            },
            {
                'index': 18,
                'name': "Aquarius",
                'keyboard_mapping': "F"
            },
            {
                'index': 19,
                'name': "Pegasus",
                'keyboard_mapping': "7"
            },
            {
                'index': 20,
                'name': "Sculptor",
                'keyboard_mapping': "c"
            },
            {
                'index': 21,
                'name': "Pisces",
                'keyboard_mapping': "W"
            },
            {
                'index': 22,
                'name': "Andromeda",
                'keyboard_mapping': "6"
            },
            {
                'index': 23,
                'name': "Triangulum",
                'keyboard_mapping': "G"
            },
            {
                'index': 24,
                'name': "Aries",
                'keyboard_mapping': "4"
            },
            {
                'index': 25,
                'name': "Perseus",
                'keyboard_mapping': "B"
            },
            {
                'index': 26,
                'name': "Cetus",
                'keyboard_mapping': "H"
            },
            {
                'index': 27,
                'name': "Taurus",
                'keyboard_mapping': "R"
            },
            {
                'index': 28,
                'name': "Auriga",
                'keyboard_mapping': "L"
            },
            {
                'index': 29,
                'name': "Eridanus",
                'keyboard_mapping': "2"
            },
            {
                'index': 30,
                'name': "Orion",
                'keyboard_mapping': "N"
            },
            {
                'index': 31,
                'name': "Canis Minor",
                'keyboard_mapping': "Q"
            },
            {
                'index': 32,
                'name': "Monoceros",
                'keyboard_mapping': "9"
            },
            {
                'index': 33,
                'name': "Gemini",
                'keyboard_mapping': "J"
            },
            {
                'index': 34,
                'name': "Hydra",
                'keyboard_mapping': "0"
            },
            {
                'index': 35,
                'name': "Lynx",
                'keyboard_mapping': "O"
            },
            {
                'index': 36,
                'name': "Cancer",
                'keyboard_mapping': "T"
            },
            {
                'index': 37,
                'name': "Sextans",
                'keyboard_mapping': "Y"
            },
            {
                'index': 38,
                'name': "Leo Minor",
                'keyboard_mapping': "1"
            },
            {
                'index': 39,
                'name': "Leo",
                'keyboard_mapping': "I"
            }
        ]

    def get_symbol_key_map(self):
        keyboard_mapping = {}
        for symbol in self.symbols:
            keyboard_mapping.update({ symbol.get('keyboard_mapping'): symbol.get('index') })
        return keyboard_mapping

    def get_all(self):
        symbols_out = []
        for symbol in self.symbols:
            new_symbol = symbol.copy()
            new_symbol['imageSrc'] = self.get_image_path(new_symbol['index'])
            symbols_out.append(new_symbol)
        return symbols_out

    def get_dhd_symbols(self):
        ret_arr = []
        for symbol in self.symbols:
            ret_symbol = symbol
            if symbol.get("is_on_dhd", True): # If the key doesn't exist, assume it's on the DHD
                ret_symbol['imageSrc'] = self.get_image_path(ret_symbol['index'])
                ret_arr.append(ret_symbol)
        return ret_arr

    def get_image_path(self, index):
        return "/chevrons/" + self.galaxy_path + "/" + str(index).zfill(3) + ".svg"

    def get_all_ddslick(self):
        symbols = self.get_all()

        symbols_out = []
        for symbol in symbols:
            if symbol.get("is_on_dhd", True): # Only show symbols that are on the DHD
                new_symbol = {
                    'text':         "",
                    'value':        symbol['index'],
                    'selected':     False,
                    'description':  symbol['name'],
                    'imageSrc':     symbol['imageSrc']
                }
                symbols_out.append(new_symbol)

        return symbols_out
    def get_name_by_index(self, index):
        return next(item for item in self.symbols if item['index'] == index)['name']
