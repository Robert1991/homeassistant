import appdaemon.plugins.hass.hassapi as hass

from dateutil import parser


class ReactivationTimer(hass.Hass):
    current_timer_handle = None

    def initialize(self):
        self.listen_state(self.start_timer,
                          self.args["observed_input_boolean"], new="off")
        self.listen_state(self.stop_timer,
                          self.args["observed_input_boolean"], new="on")

    def stop_timer(self, entity, attribute, old, new, kwargs):
        self.cancel_timer(self.current_timer_handle)

    def start_timer(self, entity, attribute, old, new, kwargs):
        time_string = self.get_state(self.args["reactivation_timeout"])
        timer_interval_datetime = parser.parse(time_string)

        timer_interval_in_seconds = timer_interval_datetime.hour * 60 * 60 + \
            timer_interval_datetime.minute * 60 + timer_interval_datetime.second

        self.current_timer_handle = self.run_in(
            self.reactivate_input_bool, timer_interval_in_seconds)

    def reactivate_input_bool(self, kwargs):
        self.log("Reactivated: " + str(self.args["reactivation_timeout"]))
        self.turn_on(self.args["observed_input_boolean"])
