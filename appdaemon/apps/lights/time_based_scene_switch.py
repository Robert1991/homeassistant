import appdaemon.plugins.hass.hassapi as hass
from dateutil import parser


class TimeBasedSceneSwitch(hass.Hass):
    running_timers = []
    observed_listeners = []

    def initialize(self):
        self.listen_state(self.refresh_listeners,
                          self.args["light_automatic_enabled"],
                          new="on")
        self.listen_event(self.refresh_listeners,
                          "homeassistant_start")

    def refresh_listeners(self, entity, attribute, old, new, kwargs):
        self.log("Received change event from: " + str(entity))
        self.log("Setting up time depended light control for: " +
                 self.args["toggled_scene_input_select"])
        self.reset()
        scenes_with_start_time = self.get_state(
            self.args["scene_switch_input_select"], attribute="options")

        for scene_start_time_tuple in scenes_with_start_time:
            scene_start_time_tuple_split = self.split_scene_start_time_tuple(
                scene_start_time_tuple)
            if scene_start_time_tuple_split:
                self.register_timer_callback(scene_start_time_tuple_split)
                self.log("Timebased light switch setup for " +
                         self.args["scene_switch_input_select"])
            else:
                self.log(
                    "Invalid scene start time input select tuple: " + scene_start_time_tuple)
        self.toggle_current_light_scene(scenes_with_start_time)

    def reset(self):
        self.clear_current_observations()
        self.clear_running_timers()

    def split_scene_start_time_tuple(self, scene_start_time_tuple):
        scene_start_time_tuple_split = scene_start_time_tuple.split('/')
        if len(scene_start_time_tuple_split) == 2:
            return scene_start_time_tuple_split
        return None

    def register_timer_callback(self, scene_start_time_array):
        scene_start_time_entity = self.get_scene_start_time_entity(
            scene_start_time_array)
        toggled_scene_entity = self.get_scene_input_select_entity(
            scene_start_time_array)
        if scene_start_time_entity and toggled_scene_entity:
            scene_start_time = self.get_scene_start_time(
                scene_start_time_entity)
            toggled_scene = self.get_state(toggled_scene_entity)
            timer_callback = self.run_daily(self.toggle_scene,
                                            scene_start_time.time(), scene=toggled_scene)
            self.running_timers.append(timer_callback)
            self.listen_to(scene_start_time_entity)
            self.listen_to(toggled_scene_entity)
        else:
            self.log("Scene start time not set on input_datetime." +
                     scene_start_time_entity)

    def toggle_current_light_scene(self, scenes_with_start_time):
        current_toggled_scene = None
        current_latest_time_scene = None
        for scene_start_time_tuple in scenes_with_start_time:
            scene_start_time_tuple_split = self.split_scene_start_time_tuple(
                scene_start_time_tuple)
            if scene_start_time_tuple_split:
                scene_start_time = self.get_scene_start_time_from_tuple(
                    scene_start_time_tuple_split)

                if scene_start_time < self.time():
                    toggled_scene = self.get_toggled_scene_from_tuple(
                        scene_start_time_tuple_split)
                    if not current_latest_time_scene:
                        current_latest_time_scene = scene_start_time
                        current_toggled_scene = toggled_scene
                    elif scene_start_time > current_latest_time_scene:
                        current_latest_time_scene = scene_start_time
                        current_toggled_scene = toggled_scene

        if current_toggled_scene:
            self.toggle_scene({"scene": current_toggled_scene})
        else:
            self.toggle_latest_beginning_scene(scenes_with_start_time)

    def toggle_latest_beginning_scene(self, scenes_with_start_time):
        current_latest_time_scene = None
        current_latest_time = None
        for scene_start_time_tuple in scenes_with_start_time:
            scene_start_time_tuple_split = self.split_scene_start_time_tuple(
                scene_start_time_tuple)
            if scene_start_time_tuple_split:
                scene_start_time = self.get_scene_start_time_from_tuple(
                    scene_start_time_tuple_split)
                toggled_scene = self.get_toggled_scene_from_tuple(
                    scene_start_time_tuple_split)
                if not current_latest_time:
                    current_latest_time = scene_start_time
                    current_latest_time_scene = toggled_scene
                elif current_latest_time < scene_start_time:
                    current_latest_time = scene_start_time
                    current_latest_time_scene = toggled_scene
            if current_latest_time_scene:
                self.toggle_scene({"scene": current_latest_time_scene})

    def toggle_scene(self, input_args):
        self.log("Toggling scene: " +
                 input_args["scene"] + " in " + self.args["toggled_scene_input_select"])
        self.select_option(
            self.args["toggled_scene_input_select"], input_args["scene"])

    def get_scene_start_time_entity(self, scene_start_time_tuple):
        if len(scene_start_time_tuple) == 2:
            return "input_datetime." + scene_start_time_tuple[0]
        return None

    def get_scene_input_select_entity(self, scene_start_time_tuple):
        if len(scene_start_time_tuple) == 2:
            return "input_select." + scene_start_time_tuple[1]
        return None

    def get_scene_start_time(self, scene_start_time_entity):
        start_time = self.get_state(scene_start_time_entity)
        return parser.parse(start_time)

    def get_toggled_scene_from_tuple(self, scene_start_time_tuple):
        input_select = self.get_scene_input_select_entity(
            scene_start_time_tuple)
        if input_select:
            return self.get_state(input_select)
        return None

    def get_scene_start_time_from_tuple(self, scene_start_time_tuple):
        start_time_entity = self.get_scene_start_time_entity(
            scene_start_time_tuple)
        if start_time_entity:
            return self.get_scene_start_time(start_time_entity).time()
        return None

    def listen_to(self, entity):
        listener = self.listen_state(self.refresh_listeners,
                                     entity)
        self.observed_listeners.append(listener)

    def clear_current_observations(self):
        for timer in self.running_timers:
            self.cancel_timer(timer)
        self.running_timers = []

    def clear_running_timers(self):
        for observed_entity in self.observed_listeners:
            self.cancel_listen_state(observed_entity)
        self.observed_listeners = []
