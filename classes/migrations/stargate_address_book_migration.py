from stargate_config import StargateConfig
from stargate_address_book import StargateAddressBook
from ancients_log_book import AncientsLogBook

from stargate_address import local_stargate_address # pylint: disable=import-error
from stargate_address import fan_gates_cfg          # pylint: disable=import-error
from hardcoded_addresses import known_planets       # pylint: disable=import-error

# pylint: disable=too-few-public-methods

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
        self.address_book = StargateAddressBook(self)

        ### Run the migration
        self.migrate()

    def migrate(self):
        # Clear out the existing config
        print("(Re)initializing StargateAddressBook datastore")
        self.address_book.initialize_storage()

        # Get the local stargate address, set it in the cfg
        print(f"Migrating Local Address: {local_stargate_address}" )
        self.address_book.set_local_address(local_stargate_address)

        # Loop over the fan_gates_cfg dictionary, insert into cfg
        for name, value in fan_gates_cfg.items():
            print(f"Migrating Fan Gate: {name}")
            address = value[0]
            _ip_address = value[1]
            is_black_hole = False
            self.address_book.set_fan_gate(name, address, _ip_address, is_black_hole)

        # Loop over the fan_gates_cfg dictionary, insert into cfg
        for name, gate_address in known_planets.items():
            print(f"Migrating Known Planet Gate: {name}")
            is_bh = False
            if name == "P3W-451":
                is_bh = True

            self.address_book.set_standard_gate(name, gate_address, is_black_hole=is_bh )
        print("Done.")
