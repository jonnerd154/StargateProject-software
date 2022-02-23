
class StargateSymbolManager:

    def __init__(self):
        self.symbols = None
        self.init()

    def get_all_ddslick(self):
        symbols = self.get_all()

        symbols_out = []
        for symbol in symbols:
            new_symbol = {
                'text':         "",
                'value':        symbol['index'],
                'selected':     False,
                'description':  symbol['name'],
                'imageSrc':     "/chevrons/milky_way/" + str(symbol['index']).zfill(3) + ".svg"
            }
            symbols_out.append(new_symbol)

        return symbols_out

    def init(self):
        self.symbols = [
            {
                'index': 1,
                'name': "Earth"
            },
            {
                'index': 2,
                'name': "Crater"
            },
            {
                'index': 3,
                'name': "Virgo"
            },
            {
                'index': 4,
                'name': "Bootes"
            },
            {
                'index': 5,
                'name': "Centaurus"
            },
            {
                'index': 6,
                'name': "Libra"
            },
            {
                'index': 7,
                'name': "Serpens Caput"
            },
            {
                'index': 8,
                'name': "Norma"
            },
            {
                'index': 9,
                'name': "Scorpio"
            },
            {
                'index': 10,
                'name': "Cra"
            },
            {
                'index': 11,
                'name': "Scutum"
            },
            {
                'index': 12,
                'name': "Sagittarius"
            },
            {
                'index': 13,
                'name': "Aquila"
            },
            {
                'index': 14,
                'name': "Mic"
            },
            {
                'index': 15,
                'name': "Capricorn"
            },
            {
                'index': 16,
                'name': "Pisces Austrinus"
            },
            {
                'index': 17,
                'name': "Equuleus"
            },
            {
                'index': 18,
                'name': "Aquarius"
            },
            {
                'index': 19,
                'name': "Pegasus"
            },
            {
                'index': 20,
                'name': "Sculptor"
            },
            {
                'index': 21,
                'name': "Pisces"
            },
            {
                'index': 22,
                'name': "Andromeda"
            },
            {
                'index': 23,
                'name': "Triangulum"
            },
            {
                'index': 24,
                'name': "Aries"
            },
            {
                'index': 25,
                'name': "Perseus"
            },
            {
                'index': 26,
                'name': "Cetus"
            },
            {
                'index': 27,
                'name': "Taurus"
            },
            {
                'index': 28,
                'name': "Auriga"
            },
            {
                'index': 29,
                'name': "Eridanus"
            },
            {
                'index': 30,
                'name': "Orion"
            },
            {
                'index': 31,
                'name': "Canis Minor"
            },
            {
                'index': 32,
                'name': "Monoceros"
            },
            {
                'index': 33,
                'name': "Gemini"
            },
            {
                'index': 34,
                'name': "Hydra"
            },
            {
                'index': 35,
                'name': "Lynx"
            },

            {
                'index': 36,
                'name': "Cancer"
            },
            {
                'index': 37,
                'name': "Sextans"
            },
            {
                'index': 38,
                'name': "Leo Minor"
            },
            {
                'index': 39,
                'name': "Leo"
            }
        ]

    def get_all(self):
        return self.symbols

    def get_name_by_index(self, index):
        return next(item for item in self.symbols if item['index'] == index)['name']
