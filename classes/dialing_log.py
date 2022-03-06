from datetime import datetime,timezone

class DialingLog():

    def __init__(self, stargate):
        self.log = stargate.log
        self.cfg = stargate.cfg

        self.addr_manager = stargate.addr_manager

        self.__reset_state()

    def dialing_fail(self, address_buffer):
        self.activity_start_time = self.__get_time_now()
        self.activity_end_time = self.activity_start_time
        self.dialer_address = self.addr_manager.get_book().get_local_address()
        self.receiver_address = address_buffer

        # Persist this activity
        self.log.log("Dialing Log: Failed Outbound Dialing")
        # self.log.log(f"   Start Time: {self.activity_start_time}")
        # self.log.log(f"   End Time: {self.activity_end_time}")
        self.log.log(f"   Dialer Address: {self.dialer_address}")
        self.log.log(f"   Address Buffer: {self.receiver_address}")

    def established_inbound(self, dialing_gate_address):
        self.current_activity = "Inbound"
        self.activity_start_time = self.__get_time_now()
        self.dialer_address = dialing_gate_address
        self.receiver_address = self.addr_manager.get_book().get_local_address()
        self.log.log("Dialing Log: Established Inbound")

    def established_outbound(self, receiver_address):
        self.current_activity = "Outbound"
        self.activity_start_time = self.__get_time_now()
        self.dialer_address = self.addr_manager.get_book().get_local_address()
        self.receiver_address = receiver_address
        self.log.log("Dialing Log: Established Outbound")

    def shutdown(self):

        # Just return if we don't have an established activity (on boot)
        if (self.current_activity is None):
            self.log.log("Gate is idle.")
            return

        # Log the shutdown time
        self.activity_end_time = self.__get_time_now()
        elapsed = self.__get_minutes_elapsed( self.activity_start_time, self.activity_end_time )

        self.log.log("Dialing Log: Shutdown")

        # Persist this activity
        self.log.log(f"   Activity: {self.current_activity}")
        self.log.log(f"   Gate Type: {self.address_type}")
        self.log.log(f"   Start Time: {self.activity_start_time}")
        self.log.log(f"   End Time: {self.activity_end_time}")
        self.log.log(f"   Elapsed: {elapsed} minutes")
        self.log.log(f"   Dialer Address: {self.dialer_address}")
        self.log.log(f"   Receiver Address: {self.receiver_address}")

        # Reset the state vars to get ready for the next activity
        self.__reset_state()

    def __reset_state(self):
        self.current_activity = None
        self.address_type = None
        self.activity_start_time = None
        self.dialer_address = None
        self.receiver_address = None
        self.log.log("Dialing Log: Idle")

    def __get_time_now(self):
        return datetime.now(timezone.utc)

    def __get_minutes_elapsed(self, start, end):
        diff = end - start
        minutes = diff.total_seconds() / 60
        return minutes
