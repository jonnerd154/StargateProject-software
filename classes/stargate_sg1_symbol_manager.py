
class StargateSG1SymbolManager:

    def __init__(self):
        pass

    def get_all_ddslick(self):
        symbols = self.get_all()

        symbols_out = []
        for symbol in symbols:
            new_symbol = {
                'text':         "",
                'value':        symbol['index'],
                'selected':     False,
                'description':  symbol['name'],
                'imageSrc':     "/chevrons/" + str(symbol['index']).zfill(3) + ".svg"
            }
            symbols_out.append(new_symbol)

        return symbols_out

    def get_all(self):
        return [
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
            }
        ]
