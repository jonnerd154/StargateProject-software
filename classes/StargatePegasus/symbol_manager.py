
class StargateSymbolManager:

    def __init__(self, galaxy_path):
        self.galaxy_path = galaxy_path

        self.symbols = None
        self.init_symbol_list()

    def init_symbol_list(self):

        # TODO: Update these for the Pegasus symbol set

        self.symbols = [
            {
                'index': 1,
                'name': "Acjesis"
            },
            {
                'index': 2,
                'name': "Lenchan"
            },
            {
                'index': 3,
                'name': "Alura"
            },
            {
                'index': 4,
                'name': "Ca Po"
            },
            {
                'index': 5,
                'name': "Laylox"
            },
            {
                'index': 6,
                'name': "Ecrumig"
            },
            {
                'index': 7,
                'name': "Avoniv"
            },
            {
                'index': 8,
                'name': "Bydo"
            },
            {
                'index': 9,
                'name': "Aaxel"
            },
            {
                'index': 10,
                'name': "Aldeni"
            },
            {
                'index': 11,
                'name': "Setas"
            },
            {
                'index': 12,
                'name': "Arami"
            },
            {
                'index': 13,
                'name': "Danami",
            },
            {
                'index': 14,
                'name': "Unknown Constellation"
            },
            {
                'index': 15,
                'name': "Robandus"
            },
            {
                'index': 16,
                'name': "Recktic"
            },
            {
                'index': 17,
                'name': "Zamilloz"
            },
            {
                'index': 18,
                'name': "Subido"
            },
            {
                'index': 19,
                'name': "Dawnre"
            },
            {
                'index': 20,
                'name': "Salma"
            },
            {
                'index': 21,
                'name': "Hamlinto"
            },
            {
                'index': 22,
                'name': "Elenami"
            },
            {
                'index': 23,
                'name': "Tahnan"
            },
            {
                'index': 24,
                'name': "Zeo"
            },
            {
                'index': 25,
                'name': "Roehi"
            },
            {
                'index': 26,
                'name': "Once el"
            },
            {
                'index': 27,
                'name': "Baselai"
            },
            {
                'index': 28,
                'name': "Sandovi"
            },
            {
                'index': 29,
                'name': "Illume"
            },
            {
                'index': 30,
                'name': "Amiwill"
            },
            {
                'index': 31,
                'name': "Sibbron"
            },
            {
                'index': 32,
                'name': "Gilltin"
            },
            {
                'index': 33,
                'name': "Unknown Constellation #2"
            },
            {
                'index': 34,
                'name': "Ramnon"
            },
            {
                'index': 35,
                'name': "Olavii"
            },
            {
                'index': 36,
                'name': "Hacemil"
            },
            {
                'index': 37,
                'name': "Poco Re"
            },
            {
                'index': 38,
                'name': "Abrin"
            }
        ]

    def get_all(self):
        return self.symbols

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
            new_symbol = {
                'text':         "",
                'value':        symbol['index'],
                'selected':     False,
                'description':  symbol['name'],
                'imageSrc':     self.get_image_path(symbol['index']) + ".svg"
            }
            symbols_out.append(new_symbol)

        return symbols_out
    def get_name_by_index(self, index):
        return next(item for item in self.symbols if item['index'] == index)['name']
