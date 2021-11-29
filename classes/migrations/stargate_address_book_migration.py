from stargate_config import StargateConfig
from stargate_address_book import StargateAddressBook
from ancients_log_book import AncientsLogBook

from stargate_address import local_stargate_address
from stargate_address import fan_gates_cfg
from hardcoded_addresses import known_planets

class StargateAddressBookMigration():
    def __init__(self, base_path):
        
        ### Get the directory base_path    
        self.base_path = base_path
            
        ### Load our config file
        self.cfg = StargateConfig(self.base_path, "config.json")
        
        ### Setup the logger
        self.log = AncientsLogBook(self.base_path, "sg1.log")
        self.cfg.set_log(self.log)
        self.cfg.load()
        
        ### Initialize the Address Book
        self.addressBook = StargateAddressBook(self)
        
        ### Run the migration
        self.migrate()

    def migrate(self):
        # Clear out the existing config
        print("(Re)initializing Stargate AddressBook datastore")
        self.addressBook.initialize_storage()
        
        # Get the local stargate address, set it in the cfg
        print("Migrating Local Address: {}".format(local_stargate_address) )
        self.addressBook.set_local_address(local_stargate_address)

        # Loop over the fan_gates_cfg dictionary, insert into cfg
        for name, value in fan_gates_cfg.items():
            print("Migrating Fan Gate: {}".format(name) )
            address = value[0]
            ip = value[1]
            self.addressBook.set_fan_gate(name, address, ip)
        
        # Loop over the fan_gates_cfg dictionary, insert into cfg
        for name, address in known_planets.items():
            print("Migrating Known Planet Gate: {}".format(name) )
            self.addressBook.set_standard_gate(name, address)
        print("Done.")