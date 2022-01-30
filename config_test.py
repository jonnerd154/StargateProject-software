import os
import sys
from pprint import pprint

sys.path.append('classes')
sys.path.append('config')

from stargate_config import StargateConfig
from ancients_log_book import AncientsLogBook

# Get the base path of execution - this is used in various places when working with files
base_path = os.path.split(os.path.abspath(__file__))[0]

### Load our config file.
cfg = StargateConfig(base_path, "config.json")

### Setup the logger. If we're in systemd, don't print to the console.
log = AncientsLogBook(base_path, "sg1.log", print_to_console = True )
cfg.set_log(log)
cfg.load()


# pprint(cfg.set("enable_software_updates", True))
# pprint(cfg.get_full_config_by_key("enable_software_updates"))
# pprint(cfg.set("enable_software_updates", False))
# pprint(cfg.get_full_config_by_key("enable_software_updates"))
#
# # Test type match
# try:
#     pprint(cfg.set("enable_software_updates", "500"))
#     pprint(cfg.get_full_config_by_key("enable_software_updates"))
# except ValueError as ex:
#     print(f"Exception: {ex}")
#
# old = cfg.get("chevron_mapping")
# pprint(old)
# pprint(cfg.get_full_config_by_key("chevron_mapping"))
#
# volume_as_percent = cfg.get("volume_as_percent")
# pprint(volume_as_percent)
#
# volume_as_percent = cfg.set("volume_as_percent", 55)
#
# volume_as_percent = cfg.get("volume_as_percent")
# pprint(volume_as_percent)
#
# volume_as_percent = cfg.set("volume_as_percent", 50)
#
# volume_as_percent = cfg.get("volume_as_percent")
# pprint(volume_as_percent)
# try:
#     cfg.set("volume_as_percent", -1)
#     pprint(cfg.get("volume_as_percent"))
# except ValueError as ex:
#     print(f"Exception: {ex}")
