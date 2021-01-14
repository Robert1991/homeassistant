import appdaemon.plugins.hass.hassapi as hass


class IkeaLightSwitch(hass.Hass):
    def initialize(self):
        self.listen_state(self.toggle_light_group,
                          self.args["light_switch_sensor"], new="toggle")
        self.listen_state(self.increase_brightness,
                          self.args["light_switch_sensor"], new="brightness_up_click")
        self.listen_state(self.decrease_brightness,
                          self.args["light_switch_sensor"], new="brightness_down_click")
        self.listen_state(self.switch_to_previous_scene,
                          self.args["light_switch_sensor"], new="arrow_left_click")
        self.listen_state(self.switch_to_next_scene,
                          self.args["light_switch_sensor"], new="arrow_right_click")

    def toggle_light_group(self, entity, attribute, old, new, kwargs):
        if self.get_state(self.args["light_group"]) == "on":
            self.turn_off(self.args["light_group"])
            return
        self.turn_on(self.args["light_group"])

    def decrease_brightness(self, entity, attribute, old, new, kwargs):
        if self.get_state(self.args["light_group"]) == "off":
            self.turn_on(self.args["light_group"])
            return
        dim_step_size = self.get_current_dim_step_size()
        for light in self.get_state(self.args["light_group"], attribute="entity_id"):
            if self.get_state(light) == "on":
                current_brightness = self.get_current_light_brightness(light)
                if current_brightness:
                    new_brightness = current_brightness - dim_step_size
                    if new_brightness < 0:
                        self.turn_off(light)
                    else:
                        self.turn_on(light, brightness=new_brightness)

    def increase_brightness(self, entity, attribute, old, new, kwargs):
        if self.get_state(self.args["light_group"]) == "off":
            self.turn_on(self.args["light_group"])
            return
        dim_step_size = self.get_current_dim_step_size()
        for light in self.get_state(self.args["light_group"], attribute="entity_id"):
            if self.get_state(light) == "on":
                current_brightness = self.get_current_light_brightness(light)
                if current_brightness:
                    new_brightness = current_brightness + dim_step_size
                    if new_brightness > 255:
                        new_brightness = 255
                    self.turn_on(light, brightness=new_brightness)

    def switch_to_next_scene(self, entity, attribute, old, new, kwargs):
        self.call_service("input_select/select_next",
                          entity_id=self.args["scene_input_select"])
        current_selected = self.get_state(
            self.args["scene_input_select"]).lower()
        scene_entity = "scene." + self.args["scene_prefix"].lower() \
            + "_" + current_selected.replace(" ", "_")
        self.call_service("scene/turn_on",
                          entity_id=scene_entity)

    def switch_to_previous_scene(self, entity, attribute, old, new, kwargs):
        self.call_service("input_select/select_previous",
                          entity_id=self.args["scene_input_select"])
        current_selected = self.get_state(
            self.args["scene_input_select"]).lower()
        scene_entity = "scene." + self.args["scene_prefix"].lower() \
            + "_" + current_selected.replace(" ", "_")
        self.call_service("scene/turn_on",
                          entity_id=scene_entity)

    def create_scene_enitity_id(self):
        current_selected = self.get_state(
            self.args["scene_input_select"]).lower()
        return "scene." + self.args["scene_prefix"].lower() \
            + "_" + current_selected.replace(" ", "_")

    def get_current_light_brightness(self, light_entity_id):
        brightness = self.get_state(light_entity_id, attribute="brightness")
        if brightness:
            return int(float(brightness))
        return None

    def get_current_dim_step_size(self):
        return int(float(self.get_state(self.args["dim_step_size"])))
