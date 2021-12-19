from stargate_config import StargateConfig

class StargateAddressBook:

    def __init__(self, manager):

        self.manager = manager
        self.cfg = manager.cfg
        self.base_path = manager.base_path
        self.log = manager.log
        
        # Initialize the Config
        self.datastore = StargateConfig(self.base_path, "addresses.json")
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
        else:
            return False
            
    def set_local_address(self, address):
        # TODO: Validate address
        # TODO: Ensure unique address
        self.datastore.set("local_stargate_address", address)
    
    def get_local_loopback_address(self):
        return self.datastore.get("local_stargate_address_loopback") # Equivalent to 127.0.0.1
        
    # ----

    def get_entry_by_address(self, address):
        #print("Searching Address Book for {}".format(address))
        found_standard_gate = self.get_standard_gate_by_address(address)
        if found_standard_gate:
            return found_standard_gate
        
        found_fan_gate = self.get_fan_gate_by_address(address)
        if found_fan_gate:
            return found_standard_gate
        
        return False 
    
    def get_all_nonlocal_addresses(self):
        fan_gates = self.get_fan_gates()
        standard_gates = self.get_standard_gates()
        all_gates = {**fan_gates, **standard_gates}
        return all_gates 
         
    # ----
        
    def get_fan_gates(self):
        return self.datastore.get("fan_gates")   
    
    def get_fan_gate_by_address(self, address):
        for key, value in self.get_fan_gates().items():
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

    def get_standard_gates(self):
        return self.datastore.get("standard_gates") 
    
    def get_standard_gate_by_address(self, address):
        for key, value in self.get_standard_gates().items():
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
            
