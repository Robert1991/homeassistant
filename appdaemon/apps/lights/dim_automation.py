import appdaemon.plugins.hass.hassapi as hass
from time import sleep


class DimLights(hass.Hass):
    def initialize(self):
        self.listen_state(self.toggle_event,
                          self.args["light_group"], new="on")
        self.listen_state(self.toggle_event,
                          self.args["light_group"], attribute="brightness")
        self.listen_state(self.toggle_event, self.args["light_intensity_toggle_threshold"])
        self.listen_state(self.toggle_event,
                          self.args["enable_automation_input"])
        self.listen_state(self.toggle_event,
                          self.args["light_turn_off_boundary_brightness"])

    def toggle_event(self, entity, attribute, old, new, kwargs):
        if not self.check_if_light_needs_to_be_dimmed(entity):
            return
        lights_in_group = self.get_state(
            self.args["light_group"], attribute="entity_id")
        turned_off_lights = set()
        sleep(1)
        light_turn_out_boundary = self.read_state_as_float(
            self.args['light_turn_off_boundary_brightness'])
        while self.read_light_sensor_state() > self.read_light_threshold() and len(turned_off_lights) < len(lights_in_group):
            for light in lights_in_group:
                if self.get_state(light) == "on":
                    new_light_brightness = self.calculate_new_light_brightness(
                        light)
                    if new_light_brightness > light_turn_out_boundary:
                        self.turn_on(light, brightness=new_light_brightness)
                    else:
                        turned_off_lights.add(light)
                        self.turn_off(light)
                else:
                    turned_off_lights.add(light)
            sleep(1)

    def check_if_light_needs_to_be_dimmed(self, entity):
        light_group_is_on = self.get_state(self.args["light_group"]) == "on"
        automation_is_enabled = self.get_state(
            self.args["enable_automation_input"]) == 'on'
        return light_group_is_on and automation_is_enabled

    def read_light_sensor_state(self):
        return self.read_state_as_float(self.args["light_sensor"])

    def read_light_threshold(self):
        return self.read_state_as_float(self.args["light_intensity_toggle_threshold"])

    def calculate_new_light_brightness(self, light_entity_id):
        current_light_brightness = self.get_state(
            light_entity_id, attribute="brightness")
        return float(current_light_brightness - self.read_state_as_float(
            self.args["light_turn_off_step_size"]))

    def read_state_as_float(self, entity):
        return float(self.get_state(entity))
