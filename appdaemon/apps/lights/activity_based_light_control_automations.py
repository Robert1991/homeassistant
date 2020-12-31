import appdaemon.plugins.hass.hassapi as hass


class TurnOffAutomation(hass.Hass):
    current_timer = None

    def initialize(self):
        self.listen_state(self.start_turn_off_lights_timer,
                          self.args["observed_activity_sensor"], new="off")
        self.listen_state(self.stop_turn_off_lights_timer,
                          self.args["observed_activity_sensor"], new="on")

    def start_turn_off_lights_timer(self, entity, attribute, old, new, kwargs):
        timeout = int(float(self.get_state(self.args["turn_off_timeout"])))
        self.current_timer = self.run_in(
            self.turn_off_light_group, int(timeout))

    def stop_turn_off_lights_timer(self, entity, attribute, old, new, kwargs):
        self.cancel_timer(self.current_timer)

    def turn_off_light_group(self, kwargs):
        self.turn_off(self.args["light_group"])


class TurnOnAutomation(hass.Hass):
    def initialize(self):
        self.listen_state(self.turn_on_lights,
                          self.args["observed_activity_sensor"], new="on")

    def turn_on_lights(self, entity, attribute, old, new, kwargs):
        automation_start_time = self.read_state_from_input_arg(
            "light_automation_start_time")
        automation_end_time = self.read_state_from_input_arg(
            "light_automation_end_time")
        time_dependend_control_disabled = self.read_state_from_input_arg(
            'enable_time_depended_automation_input') == 'off'
        if self.now_is_between(automation_start_time, automation_end_time) or time_dependend_control_disabled:
            light_sensor_state = self.read_state_as_float_from_input_arg(
                "light_sensor")
            light_threshold = self.read_state_as_float_from_input_arg(
                "light_intensity_toggle_threshold")
            lights_are_on = self.read_state_from_input_arg(
                "light_group") == "on"
            if (light_sensor_state <= light_threshold and not lights_are_on):
                if self.read_state_from_input_arg("enable_automatic_scene_mode") == "on":
                    self.turn_on_current_scene()
                else:
                    self.turn_on(self.args["light_group"])

    def turn_on_current_scene(self):
        scene_prefix = self.args["scene_group_prefix"]
        current_select_scene_display_name = self.read_state_from_input_arg(
            "scene_input_select")
        scene_entity_id = self.format_scene_name(
            scene_prefix, current_select_scene_display_name)
        self.turn_on(scene_entity_id)

    def format_scene_name(self, scene_prefix, scene_friendly_post_fix):
        scene_friendly_post_fix_cleaned = scene_friendly_post_fix.lower().replace(" ", "_")
        scene_prefix_cleaned = scene_prefix.lower()
        return "scene." + scene_prefix_cleaned + "_" + scene_friendly_post_fix_cleaned

    def read_state_as_float_from_input_arg(self, input_arg):
        return float(self.read_state_from_input_arg(input_arg))

    def read_state_from_input_arg(self, input_arg):
        return self.get_state(self.args[input_arg])
