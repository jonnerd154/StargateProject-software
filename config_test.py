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


# pprint(cfg.set("software_update_enabled", True))
# pprint(cfg.get_full_config_by_key("software_update_enabled"))
# pprint(cfg.set("software_update_enabled", False))
# pprint(cfg.get_full_config_by_key("software_update_enabled"))
#
# # Test type match
# try:
#     pprint(cfg.set("software_update_enabled", "500"))
#     pprint(cfg.get_full_config_by_key("software_update_enabled"))
# except ValueError as ex:
#     print(f"Exception: {ex}")
#
# old = cfg.get("chevron_config")
# pprint(old)
# pprint(cfg.get_full_config_by_key("chevron_config"))
#
# audio_volume = cfg.get("audio_volume")
# pprint(audio_volume)
#
# audio_volume = cfg.set("audio_volume", 55)
#
# audio_volume = cfg.get("audio_volume")
# pprint(audio_volume)
#
# audio_volume = cfg.set("audio_volume", 50)
#
# audio_volume = cfg.get("audio_volume")
# pprint(audio_volume)
# try:
#     cfg.set("audio_volume", -1)
#     pprint(cfg.get("audio_volume"))
# except ValueError as ex:
#     print(f"Exception: {ex}")
