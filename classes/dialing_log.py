from datetime import datetime,timezone
from stargate_config import StargateConfig
import rollbar

class DialingLog():

    def __init__(self, stargate):
        self.log = stargate.log
        self.cfg = stargate.cfg

        self.addr_manager = stargate.addr_manager

        self.current_activity = {}
        self.summary = {}

        # Initialize the Config
        self.base_path = stargate.base_path
        self.galaxy_path = stargate.galaxy_path
        self.datastore = StargateConfig(self.base_path, "dialing_log", self.galaxy_path)
        self.datastore.set_log(self.log)
        self.datastore.load()

        self.__reset_state()

    def __reset_summary_storage(self): # pylint: disable=unused-private-member

        self.datastore.set("established_standard_count", 0)    # Lifetime Count of Established Outbound Wormholes to Movie Gates
        self.datastore.set("established_standard_mins", 0)    # Lifetime Minutes Outbound Established to Movie Gates

        self.datastore.set("established_fan_count", 0)         # Lifetime Count of Established Outbound Wormholes to Fan Gates
        self.datastore.set("established_fan_mins", 0)          # Lifetime Minutes Outbound Established to Fan Gates

        self.datastore.set("inbound_count", 0)                 # Lifetime Count of Established Inbound Wormholes
        self.datastore.set("inbound_mins", 0)                  # Lifetime Minutes Inbound Established

        self.datastore.set("dialing_failures", 0)              # Lifetime Failed Dialing Attempts

    def get_summary(self):
        return self.datastore.get_all_configs()

    def dialing_fail(self, address_buffer):
        self.current_activity['start_time'] = self.__get_time_now()
        self.current_activity['end_time'] = self.current_activity['start_time']
        self.current_activity['dialer_address'] = self.addr_manager.get_book().get_local_address()
        self.current_activity['receiver_address'] = address_buffer

        # Persist this activity
        self.log.log("Dialing Log: Failed Outbound Dialing")
        # self.log.log(f"   Start Time: {self.activity_start_time}")
        # self.log.log(f"   End Time: {self.activity_end_time}")
        self.log.log(f"   Dialer Address: {self.current_activity['dialer_address']}")
        self.log.log(f"   Address Buffer: {self.current_activity['receiver_address']}")

        # Update the Summary
        self.datastore.set('dialing_failures', self.datastore.get('dialing_failures') + 1)

        # Update Rollbar
        rollbar.report_message('Failed Outbound Dialing', 'info')

    def established_inbound(self, dialing_gate_address):
        self.current_activity['activity'] = "Inbound"
        self.current_activity['start_time'] = self.__get_time_now()
        self.current_activity['dialer_address'] = dialing_gate_address
        self.current_activity['receiver_address'] = self.addr_manager.get_book().get_local_address()
        self.log.log("Dialing Log: Established Inbound")

        # Update the Summary
        self.summary['inbound_count'] += 1
        self.datastore.set('inbound_count', self.datastore.get('inbound_count') + 1)

        # Update Rollbar
        rollbar.report_message('Established Inbound', 'info')

    def established_outbound(self, receiver_address):
        self.current_activity['activity'] = "Outbound"
        self.current_activity['start_time'] = self.__get_time_now()
        self.current_activity['dialer_address']= self.addr_manager.get_book().get_local_address()
        self.current_activity['receiver_address'] = receiver_address
        self.current_activity['remote_gate_type'] = "FAN" if self.addr_manager.is_fan_made_stargate(receiver_address) else "MOVIE"

        if self.current_activity['remote_gate_type'] == "FAN":
            self.datastore.set('established_fan_count', self.datastore.get('established_fan_count') + 1)
        else:
            self.datastore.set('established_standard_count', self.datastore.get('established_standard_count') + 1)

        self.log.log("Dialing Log: Established Outbound")

        # Update Rollbar
        rollbar.report_message('Established Outbound', 'info')

    def shutdown(self):

        # Just return if we don't have an established activity (on boot)
        if self.current_activity['activity'] is None:
            self.log.log("Gate is idle.")
            return

        # Log the shutdown time and calculate time established
        self.current_activity['end_time'] = self.__get_time_now()
        elapsed = self.__get_minutes_elapsed()

        self.log.log("Dialing Log: Shutdown")

        # Persist this activity
        self.log.log(f"   Activity: {self.current_activity['activity']}")
        self.log.log(f"   Gate Type: {self.current_activity['remote_gate_type']}")
        self.log.log(f"   Start Time: {self.current_activity['start_time']}")
        self.log.log(f"   End Time: {self.current_activity['end_time']}")
        self.log.log(f"   Elapsed: {elapsed} minutes")
        self.log.log(f"   Dialer Address: {self.current_activity['dialer_address']}")
        self.log.log(f"   Receiver Address: {self.current_activity['receiver_address']}")

        if self.current_activity['activity'] == "Outbound":
            if self.current_activity['remote_gate_type'] == "FAN":
                self.datastore.set('established_fan_mins', self.datastore.get('established_fan_mins') + elapsed)
            else: # standard/movie
                self.datastore.set('established_standard_mins', self.datastore.get('established_standard_mins') + elapsed)
        else: # Inbound
            self.datastore.set('inbound_mins', self.datastore.get('inbound_mins') + elapsed)

        # Update Rollbar
        rollbar.report_message('Disengaged', 'info')

        # Reset the state vars to get ready for the next activity
        self.__reset_state()

    def __reset_state(self):
        self.current_activity['activity'] = None
        self.current_activity['remove_address_type'] = None
        self.current_activity['start_time'] = None
        self.current_activity['dialer_address'] = None
        self.current_activity['receiver_address'] = None
        self.log.log("Dialing Log: Idle")

        # Update Rollbar
        rollbar.report_message('Gate Idle', 'info')

    @staticmethod
    def __get_time_now():
        return datetime.now(timezone.utc)

    def __get_minutes_elapsed(self):
        diff = self.current_activity['end_time'] - self.current_activity['start_time']
        minutes = diff.total_seconds() / 60
        return minutes
