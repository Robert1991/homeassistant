from apps.lights.activity_based_light_control_automations import TurnOnAutomation
from apps.lights.activity_based_light_control_automations import TurnOffAutomation
from appdaemontestframework import automation_fixture
from mock import patch
from datetime import datetime


@automation_fixture(TurnOnAutomation)
def turn_on_lights(given_that):
    given_that.passed_arg('enable_automatic_scene_mode').is_set_to(
        'input_boolean.bedroom_automatic_scene_mode_enabled')
    given_that.passed_arg('enable_time_depended_automation_input').is_set_to(
        'input_boolean.some_enable_time_automatic_switch')
    given_that.passed_arg('light_group').is_set_to('light.some_light_group')
    given_that.passed_arg('observed_activity_sensor').is_set_to(
        'binary_sensor.some_activity_sensor')
    given_that.passed_arg('light_intensity_toggle_threshold').is_set_to(
        'input_number.some_threshold')
    given_that.passed_arg('light_sensor').is_set_to(
        'sensor.some_light_sensor')
    given_that.passed_arg('scene_input_select').is_set_to(
        'input_select.some_scene_input_select')
    given_that.passed_arg('scene_group_prefix').is_set_to(
        'some_room')
    given_that.passed_arg('light_automation_start_time').is_set_to(
        'input_datetime.light_automation_start')
    given_that.passed_arg('light_automation_end_time').is_set_to(
        'input_datetime.light_automation_end')

    given_that.state_of('input_boolean.some_enable_time_automatic_switch').is_set_to(
        'on')
    given_that.state_of(
        'input_datetime.light_automation_start').is_set_to('09:00:00')
    given_that.state_of(
        'input_datetime.light_automation_end').is_set_to('23:00:00')
    given_that.state_of(
        'input_boolean.bedroom_automatic_scene_mode_enabled').is_set_to('on')


def now_is_between_patched_return_true(from_time, to_time):
    if from_time == "09:00:00" and to_time == "23:00:00":
        return True
    return False


def now_is_between_patched_return_false(from_time, to_time):
    if from_time == "09:00:00" and to_time == "23:00:00":
        return False
    return True


def test_turn_on_lights_when_time_dependend_control_is_deactivated(given_that, turn_on_lights, assert_that):
    given_that.state_of('input_boolean.some_enable_time_automatic_switch').is_set_to(
        'off')
    given_that.state_of('binary_sensor.some_activity_sensor').is_set_to('on')
    given_that.state_of('light.some_light_group').is_set_to('off')
    given_that.state_of('input_number.some_threshold').is_set_to('40.0')
    given_that.state_of('sensor.some_light_sensor').is_set_to('35.0')
    given_that.state_of(
        'input_select.some_scene_input_select').is_set_to('Relaxed Light')

    with patch('appdaemon.plugins.hass.hassapi.Hass.now_is_between', side_effect=now_is_between_patched_return_false):
        turn_on_lights.turn_on_lights(
            'binary_sensor.some_activity_sensor', None, None, None, None)

        assert_that('scene.some_room_relaxed_light').was.turned_on()


def test_turn_on_lights_when_there_is_movement_and_insufficient_lights(given_that, turn_on_lights, assert_that):
    given_that.state_of('binary_sensor.some_activity_sensor').is_set_to('on')
    given_that.state_of('light.some_light_group').is_set_to('off')
    given_that.state_of('input_number.some_threshold').is_set_to('40.0')
    given_that.state_of('sensor.some_light_sensor').is_set_to('30.0')
    given_that.state_of(
        'input_select.some_scene_input_select').is_set_to('Relaxed Light')

    with patch('appdaemon.plugins.hass.hassapi.Hass.now_is_between', side_effect=now_is_between_patched_return_true):
        turn_on_lights.turn_on_lights(
            'binary_sensor.some_activity_sensor', None, None, None, None)

        assert_that('scene.some_room_relaxed_light').was.turned_on()


def test_turn_on_lights_when_there_is_movement_and_insufficient_lights_scene_mode_disabled(given_that, turn_on_lights, assert_that):
    given_that.passed_arg('light_group').is_set_to('light.some_light_group')
    given_that.state_of('binary_sensor.some_activity_sensor').is_set_to('on')
    given_that.state_of('light.some_light_group').is_set_to('off')
    given_that.state_of('input_number.some_threshold').is_set_to('40.0')
    given_that.state_of('sensor.some_light_sensor').is_set_to('30.0')
    given_that.state_of(
        'input_select.some_scene_input_select').is_set_to('Relaxed Light')
    given_that.state_of(
        'input_boolean.bedroom_automatic_scene_mode_enabled').is_set_to('off')

    with patch('appdaemon.plugins.hass.hassapi.Hass.now_is_between', side_effect=now_is_between_patched_return_true):
        turn_on_lights.turn_on_lights(
            'binary_sensor.some_activity_sensor', None, None, None, None)

        assert_that('light.some_light_group').was.turned_on()
        assert_that('scene.some_room_relaxed_light').was_not.turned_on()


def test_turn_on_lights_when_there_is_movement_and_sufficient_lights(given_that, turn_on_lights, assert_that):
    given_that.time_is(datetime.strptime("10:00", "%H:%M"))
    given_that.state_of('binary_sensor.some_activity_sensor').is_set_to('on')
    given_that.state_of('light.some_light_group').is_set_to('off')
    given_that.state_of('input_number.some_threshold').is_set_to('40.0')
    given_that.state_of('sensor.some_light_sensor').is_set_to('45.0')
    given_that.state_of(
        'input_select.some_scene_input_select').is_set_to('Relaxed Light')

    with patch('appdaemon.plugins.hass.hassapi.Hass.now_is_between', side_effect=now_is_between_patched_return_true):
        turn_on_lights.turn_on_lights(
            'binary_sensor.some_activity_sensor', None, None, None, None)

        assert_that('scene.some_room_relaxed_light').was_not.turned_on()


def test_turn_on_lights_when_there_is_movement_and_insufficient_lights_but_already_on(given_that, turn_on_lights, assert_that):
    given_that.time_is("10:00:00")
    given_that.state_of('binary_sensor.some_activity_sensor').is_set_to('on')
    given_that.state_of('light.some_light_group').is_set_to('on')
    given_that.state_of('input_number.some_threshold').is_set_to('40.0')
    given_that.state_of('sensor.some_light_sensor').is_set_to('35.0')
    given_that.state_of(
        'input_select.some_scene_input_select').is_set_to('Relaxed Light')

    with patch('appdaemon.plugins.hass.hassapi.Hass.now_is_between', side_effect=now_is_between_patched_return_true):
        turn_on_lights.turn_on_lights(
            'binary_sensor.some_activity_sensor', None, None, None, None)

        assert_that('scene.some_room_relaxed_light').was_not.turned_on()


def test_turn_on_lights_when_there_is_movement_and_insufficient_but_time_span_not_met(given_that, turn_on_lights, assert_that):
    given_that.time_is("10:00:00")
    given_that.state_of('binary_sensor.some_activity_sensor').is_set_to('on')
    given_that.state_of('light.some_light_group').is_set_to('off')
    given_that.state_of('input_number.some_threshold').is_set_to('40.0')
    given_that.state_of('sensor.some_light_sensor').is_set_to('34.0')
    given_that.state_of(
        'input_select.some_scene_input_select').is_set_to('Relaxed Light')

    with patch('appdaemon.plugins.hass.hassapi.Hass.now_is_between', side_effect=now_is_between_patched_return_false):
        turn_on_lights.turn_on_lights(
            'binary_sensor.some_activity_sensor', None, None, None, None)

        assert_that('scene.some_room_relaxed_light').was_not.turned_on()


@automation_fixture(TurnOffAutomation)
def turn_off_lights(given_that):
    given_that.passed_arg('observed_activity_sensor').is_set_to(
        'binary_sensor.some_activity_sensor')
    given_that.passed_arg('turn_off_timeout').is_set_to(
        'input_number.some_turn_off_time_out')
    given_that.passed_arg('light_group').is_set_to('light.some_light_group')


def test_start_turn_off_lights_timer_turns_off_light_after_configured_input(given_that, turn_off_lights, assert_that, time_travel):
    given_that.state_of('input_number.some_turn_off_time_out') \
        .is_set_to("179.0")
    turn_off_lights.start_turn_off_lights_timer(None, None, None, None, None)
    time_travel.fast_forward(3).minutes()
    assert_that('light.some_light_group').was.turned_off()


def test_start_turn_off_lights_timer_not_turns_off_when_movement_occurs(given_that, turn_off_lights, assert_that, time_travel):
    given_that.state_of('input_number.some_turn_off_time_out') \
        .is_set_to("179.0")
    turn_off_lights.start_turn_off_lights_timer(None, None, None, None, None)
    time_travel.fast_forward(1).minutes()
    turn_off_lights.stop_turn_off_lights_timer(None, None, None, None, None)
    time_travel.fast_forward(2).minutes()
    assert_that('light.some_light_group').was_not.turned_off()
