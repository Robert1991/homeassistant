import appdaemon.plugins.hass.hassapi as hass

from time import sleep


class DimLights(hass.Hass):
    def read_state_as_float(self, entity):
        return float(self.get_state(entity))

    def read_light_sensor_state(self):
        return self.read_state_as_float(self.args["light_sensor"])

    def read_light_threshold(self):
        return self.read_state_as_float(self.args["light_threshold"])

    def initialize(self):
        self.listen_state(self.toggle_event,
                          self.args["light_group"], new="on")
        self.listen_state(self.toggle_event, self.args["light_threshold"])

    def toggle_event(self, entity, attribute, old, new, kwargs):
        if entity == self.args["light_threshold"] and self.get_state(self.args["light_group"]) == "off":
            return

        group_name = self.args["light_group"].replace("group.", "")
        lights_in_group = self.entities.group[group_name].attributes.entity_id
        turned_off_lights = set()
        sleep(1)
        while self.read_light_sensor_state() > self.read_light_threshold() and len(turned_off_lights) < len(lights_in_group):
            for light in lights_in_group:
                if self.get_state(light) == "on":
                    current_light_brightness = self.get_state(
                        light, attribute="brightness")
                    if (current_light_brightness - 5) > 1:
                        self.turn_on(light, brightness=(
                            current_light_brightness - 5))
                    else:
                        turned_off_lights.add(light)
                else:
                    turned_off_lights.add(light)
            self.log(turned_off_lights)
            sleep(1)
