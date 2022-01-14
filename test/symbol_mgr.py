import sys
sys.path.append('../classes')

from stargate_sg1_symbol_manager import StargateSG1SymbolManager
from pprint import pprint

symbolManager = StargateSG1SymbolManager()

all = symbolManager.get_all()
ddslick = symbolManager.get_all_ddslick()

pprint(all)
print("============")
pprint(ddslick)
