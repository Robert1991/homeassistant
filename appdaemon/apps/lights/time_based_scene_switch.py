import appdaemon.plugins.hass.hassapi as hass
from dateutil import parser


class TimeBasedSceneSwitch(hass.Hass):
    running_timers = []
    observed_listeners = []

    def initialize(self):
        self.listen_state(self.refresh_listeners,
                          self.args["scene_switch_input_select"])
        self.listen_state(self.refresh_listeners,
                          self.args["toggled_scene_input_select"])
        self.listen_state(self.refresh_listeners,
                          self.args["light_automatic_enabled"],
                          new="on")

    def refresh_listeners(self, entity, attribute, old, new, kwargs):
        self.reset()
        scenes_with_start_time = self.get_state(
            self.args["scene_switch_input_select"], attribute="options")

        current_scene_is_set = False
        for scene_start_time_tuple in scenes_with_start_time:
            scene_start_time_tuple_split = scene_start_time_tuple.split('/')
            if len(scene_start_time_tuple_split) == 2:
                scene_was_activated = self.register_timer_callback(
                    scene_start_time_tuple_split)
                if scene_was_activated:
                    current_scene_is_set = True
                self.log("Timebased light switch setup for " +
                         self.args["scene_switch_input_select"])
            else:
                self.log(
                    "Invalid scene start time input select tuple: " + scene_start_time_tuple)
        if not current_scene_is_set:
            self.toggle_latest_beginning_scene(scenes_with_start_time)

    def reset(self):
        self.clear_current_observations()
        self.clear_running_timers()

    def register_timer_callback(self, scene_start_time_array):
        scene_start_time_entity = "input_datetime." + scene_start_time_array[0]
        toggled_scene_input_entity = "input_select." + \
            scene_start_time_array[1]
        toggled_scene = self.get_state(toggled_scene_input_entity)
        scene_start_time = self.get_state(scene_start_time_entity)
        scene_was_activated = False
        if scene_start_time:
            scene_start_time = parser.parse(scene_start_time)
            if scene_start_time.time() < self.time():
                self.toggle_scene({"scene": toggled_scene})
                scene_was_activated = True
            timer_callback = self.run_daily(self.toggle_scene,
                                            scene_start_time.time(), scene=toggled_scene)
            self.running_timers.append(timer_callback)
            input_time_listener = self.listen_state(self.refresh_listeners,
                                                    scene_start_time_entity)
            self.observed_listeners.append(input_time_listener)
            input_select_listener = self.listen_state(self.refresh_listeners,
                                                      toggled_scene_input_entity)
            self.observed_listeners.append(input_select_listener)
        else:
            self.log("Scene start time not set on input_datetime." +
                     scene_start_time_entity)
        return scene_was_activated

    def toggle_latest_beginning_scene(self, scenes_with_start_time):
        current_latest_time_scene = None
        current_latest_time = None
        for scene_start_time_tuple in scenes_with_start_time:
            scene_start_time_tuple_split = scene_start_time_tuple.split('/')
            if len(scene_start_time_tuple_split) == 2:
                scene_start_time_str = self.get_state(
                    "input_datetime." + scene_start_time_tuple_split[0])
                scene_start_time = parser.parse(scene_start_time_str).time()
                if not current_latest_time:
                    current_latest_time = scene_start_time
                    current_latest_time_scene = scene_start_time_tuple_split[1]
                elif current_latest_time < scene_start_time:
                    current_latest_time = scene_start_time
                    current_latest_time_scene = scene_start_time_tuple_split[1]
            if current_latest_time_scene:
                light_scene_entity = self.get_state(
                    "input_select." + current_latest_time_scene)
                self.toggle_scene({"scene": light_scene_entity})

    def toggle_scene(self, input_args):
        self.log("Toggling scene: " +
                 input_args["scene"] + " in " + self.args["toggled_scene_input_select"])
        self.select_option(
            self.args["toggled_scene_input_select"], input_args["scene"])

    def clear_current_observations(self):
        for timer in self.running_timers:
            self.cancel_timer(timer)
        self.running_timers = []

    def clear_running_timers(self):
        for observed_entity in self.observed_listeners:
            self.cancel_listen_state(observed_entity)
        self.observed_listeners = []
