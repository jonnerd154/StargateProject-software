from datetime import datetime,timezone

class DialingLog():

    def __init__(self, stargate):
        self.log = stargate.log
        self.cfg = stargate.cfg

        self.addr_manager = stargate.addr_manager

        self.current_activity = {}
        self.summary = {}

        self.__reset_summary_storage()
        self.__reset_state()

    def __reset_summary_storage(self):

        self.summary['established_standard_count'] = 0    # Lifetime Count of Established Outbound Wormholes to Movie Gates
        self.summary['established_standard_mins'] = 0     # Lifetime Minutes Outbound Established to Movie Gates

        self.summary['established_fan_count'] = 0         # Lifetime Count of Established Outbound Wormholes to Fan Gates
        self.summary['established_fan_mins'] = 0          # Lifetime Minutes Outbound Established to Fan Gates

        self.summary['inbound_count'] = 0                 # Lifetime Count of Established Inbound Wormholes
        self.summary['inbound_mins'] = 0                  # Lifetime Minutes Inbound Established

        self.summary['dialing_failures'] = 0              # Lifetime Failed Dialing Attempts

    def get_summary(self):
        return self.summary

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
        self.summary['dialing_failures'] += 1

    def established_inbound(self, dialing_gate_address):
        self.current_activity['activity'] = "Inbound"
        self.current_activity['start_time'] = self.__get_time_now()
        self.current_activity['dialer_address'] = dialing_gate_address
        self.current_activity['receiver_address'] = self.addr_manager.get_book().get_local_address()
        self.log.log("Dialing Log: Established Inbound")

        self.summary['inbound_count'] += 1

    def established_outbound(self, receiver_address):
        self.current_activity['activity'] = "Outbound"
        self.current_activity['start_time'] = self.__get_time_now()
        self.current_activity['dialer_address']= self.addr_manager.get_book().get_local_address()
        self.current_activity['receiver_address'] = receiver_address
        self.current_activity['remote_gate_type'] = "MOVIE"
                # TODO: #self.addr_manager.get_type_by_address(receiver_address)

        if self.current_activity['remote_gate_type'] == "FAN":
            self.summary['established_fan_count'] += 1
        else:
            self.summary['established_standard_count'] += 1

        self.log.log("Dialing Log: Established Outbound")

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
                self.summary['established_fan_mins'] += elapsed
            else: # standard/movie
                self.summary['established_standard_mins'] += elapsed
        else: # Inbound
            self.summary['inbound_mins'] += elapsed

        # Reset the state vars to get ready for the next activity
        self.__reset_state()

    def __reset_state(self):
        self.current_activity['activity'] = None
        self.current_activity['remove_address_type'] = None
        self.current_activity['start_time'] = None
        self.current_activity['dialer_address'] = None
        self.current_activity['receiver_address'] = None
        self.log.log("Dialing Log: Idle")

    @staticmethod
    def __get_time_now():
        return datetime.now(timezone.utc)

    def __get_minutes_elapsed(self):
        diff = self.current_activity['end_time'] - self.current_activity['start_time']
        minutes = diff.total_seconds() / 60
        return minutes
