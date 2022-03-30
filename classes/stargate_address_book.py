from stargate_config import StargateConfig

class StargateAddressBook:

    def __init__(self, manager, galaxy_path):

        self.manager = manager
        self.cfg = manager.cfg
        self.base_path = manager.base_path
        self.log = manager.log

        # Initialize the Config
        self.datastore = StargateConfig(self.base_path, "addresses", galaxy_path)
        self.datastore.set_log(self.log)
        self.datastore.load()

    def initialize_storage(self):
        self.datastore.remove_all()
        self.datastore.set("local_stargate_address", None)
        self.datastore.set("fan_gates", {})
        self.datastore.set("standard_gates", {})

    # ----

    def get_local_address(self):
        return self.datastore.get("local_stargate_address")

    def get_local_address_string(self):
        if self.get_local_address() and len(self.get_local_address()) == 6:
            return "[ " + ', '.join(str(x) for x in self.get_local_address()) + " ]"

        return False

    def set_local_address(self, address):
        # TODO: Validate address
        # TODO: Ensure unique address
        self.datastore.set("local_stargate_address", address)

    def get_local_gate_name(self):
        if not self.get_local_address():
            return "Stargate"
        name = self.manager.get_planet_name_by_address( self.get_local_address() )
        if name == "Unknown Address":
            return "Stargate"

        return name

    def get_local_loopback_address(self):
        return self.datastore.get("local_stargate_address_loopback") # Equivalent to 127.0.0.1

    # ----

    def get_entry_by_address(self, address):
        #print("Searching Address Book for {}".format(address))

        found_standard_gate = self.get_standard_gate_by_address(address)
        if found_standard_gate:
            found_standard_gate['type'] = 'standard'
            return found_standard_gate

        # Check LAN Gates before Fan Gates - they take priority
        found_lan_gate = self.get_lan_gate_by_address(address)
        if found_lan_gate:
            found_lan_gate['type'] = 'lan'
            return found_lan_gate

        found_fan_gate = self.get_fan_gate_by_address(address)
        if found_fan_gate:
            found_fan_gate['type'] = 'fan'
            return found_fan_gate

        return False

    def get_all_nonlocal_addresses(self):
        fan_gates = self.get_fan_gates()
        lan_gates = self.get_lan_gates()
        standard_gates = self.get_standard_gates()
        all_gates = {**fan_gates, **lan_gates, **standard_gates}
        return all_gates

    def get_fan_and_lan_addresses(self):
        fan_gates = self.get_fan_gates()
        lan_gates = self.get_lan_gates()
        all_gates = {**fan_gates, **lan_gates}
        return all_gates

    # ----

    def get_fan_gates(self):
        gates = self.datastore.get("fan_gates").copy()
        for record in gates.values():
            record['type'] = 'fan'
        return gates

    def get_fan_gate_by_address(self, address):
        for value in self.get_fan_gates().values():
            if address == value['gate_address']:
                return value

        return False

    def set_fan_gate(self, name, gate_address, ip_address, is_black_hole=False):
        # TODO: Validate gate_address, ip_address
        # TODO: Ensure unique address
        fan_gates = self.get_fan_gates()
        fan_gates[name] = { "name": name, "gate_address": gate_address, "ip_address": ip_address, "is_black_hole": is_black_hole }
        self.datastore.set("fan_gates", fan_gates)

# ----

    def get_lan_gates(self):
        gates = self.datastore.get("lan_gates").copy()
        for record in gates.values():
            record['type'] = 'lan'
        return gates

    def get_lan_gate_by_address(self, address):
        for value in self.get_lan_gates().values():
            if address == value['gate_address']:
                return value

        return False

    def set_lan_gate(self, name, gate_address, ip_address, is_black_hole=False):
        # TODO: Validate gate_address, ip_address
        # TODO: Ensure unique address
        lan_gates = self.get_lan_gates()
        lan_gates[name] = { "name": name, "gate_address": gate_address, "ip_address": ip_address, "is_black_hole": is_black_hole }
        self.datastore.set("lan_gates", lan_gates)

    # ----

    def get_standard_gates(self):
        gates = self.datastore.get("standard_gates").copy()
        for record in gates.values():
            record['type'] = 'standard'
        return gates

    def get_standard_gate_by_address(self, address):
        for value in self.get_standard_gates().values():
            if address == value['gate_address']:
                return value
        return False

    def set_standard_gate(self, name, gate_address, is_black_hole=False):
        # TODO: Validate gate_address
        # TODO: Ensure unique address
        standard_gates = self.get_standard_gates()
        standard_gates[name] = { "name": name, "gate_address": gate_address, "is_black_hole": is_black_hole }
        self.datastore.set("standard_gates", standard_gates)

    # ----

    def is_black_hole_by_address(self, address):
        return self.get_entry_by_address( address )['is_black_hole']
