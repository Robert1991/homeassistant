import appdaemon.plugins.hass.hassapi as hass

import time

class ButtonEventHub(hass.Hass):
    pressed_time_stamp = None
    released_time_stamp = None

    last_hold_time_stamp = None

    def initialize(self):
        self.listen_state(self.pressed_button_event,
                          self.args["observed_button"], new="press")
        self.listen_state(self.released_button_event,
                          self.args["observed_button"], new="release")
        self.listen_state(self.hold_button_event,
                          self.args["observed_button"], new="hold")
    
    def pressed_button_event(self, entity, attribute, old, new, kwargs):
        self.pressed_time_stamp = self.get_now_ts()

    def released_button_event(self, entity, attribute, old, new, kwargs):
        self.released_time_stamp = self.get_now_ts()

        time_diff = self.released_time_stamp - self.pressed_time_stamp
        
        if time_diff < self.args["button_press_timeout"]:
            self.fire_event_for_button("press")
        elif self.last_hold_time_stamp:
            self.fire_event_for_button("end_hold")
        else:
            self.fire_event_for_button("release")

        self.last_hold_time_stamp = None

    def hold_button_event(self, entity, attribute, old, new, kwargs):
        self.last_hold_time_stamp = self.get_now_ts()
        self.fire_event_for_button("hold")

    def fire_event_for_button(self, event_post_fix):
        self.fire_event(self.format_event_name(event_post_fix))

    def format_event_name(self, event_post_fix):
        return self.args["observed_button"] + "_" + event_post_fix

class ButtonEventReceiver(hass.Hass):
    last_hold_up = True

    def initialize(self):
        self.listen_event(self.execute_press, self.args["observed_button"] + "_press")
        self.listen_event(self.execute_release, self.args["observed_button"] + "_release")
        self.listen_event(self.execute_hold, self.args["observed_button"] + "_hold")
        self.listen_event(self.execute_end_hold, self.args["observed_button"] + "_end_hold")
        
    def execute_press(self, entity, args, thread_info):
        self.log("press received")
    
    def execute_release(self, entity, args, thread_info):
        self.log("release received")
    
    def execute_hold(self, entity, args, thread_info):
        self.log("hold received")

        if self.last_hold_up:
            self.execute_hold_up()
        else:
            self.execute_hold_down()

    def execute_end_hold(self, entity, args, thread_info):
        self.log("end hold received")
        self.last_hold_up = not self.last_hold_up
    
    def execute_hold_up(self):
        self.log("hold_up")

    def execute_hold_down(self):
        self.log("hold_down")

class SmartLightButton(ButtonEventReceiver):
    def execute_press(self, entity, args, thread_info):
        if self.get_state(self.args["light_group"]) == "off":
            self.turn_on(self.args["light_group"])
        else:
            self.call_service("input_select/select_next", entity_id=self.args["scene_input_select"])
            current_selected = self.get_state(self.args["scene_input_select"]).lower()
            scene_entity = "scene." + self.args["scene_prefix"].lower() + "_" + current_selected.replace(" ", "_")
            time.sleep(1)
            self.call_service("scene/turn_on", entity_id=scene_entity)
    
    def execute_release(self, entity, args, thread_info):
        if self.get_state(self.args["light_group"]) == "off":
            self.turn_on(self.args["light_group"])
        else:
            self.turn_off(self.args["light_group"])


class SmartLightButtonWithDimFunction(SmartLightButton):
    def execute_hold_up(self):
        current_light_group_brightness = self.get_current_light_group_brightness()
        new_brightness = current_light_group_brightness + self.args["light_change_step_size"]
        if new_brightness <= 255:
            self.turn_on(self.args["light_group"], brightness=new_brightness)
        else:
            self.turn_on(self.args["light_group"], brightness=255)

    def execute_hold_down(self):
        current_light_group_brightness = self.get_current_light_group_brightness()
        new_brightness = current_light_group_brightness - self.args["light_change_step_size"]
        if new_brightness > 0:
            self.turn_on(self.args["light_group"], brightness=new_brightness)
        else:
            self.turn_on(self.args["light_group"], brightness=1)

    def get_current_light_group_brightness(self):
        return self.get_state(self.args["light_group"], attribute="brightness")