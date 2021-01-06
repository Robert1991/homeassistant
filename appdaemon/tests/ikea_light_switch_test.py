from apps.lights.ikea_light_switch import IkeaLightSwitch

import pytest
from appdaemontestframework import automation_fixture


@automation_fixture(IkeaLightSwitch)
def light_switch(given_that):
    given_that.passed_arg('light_switch_sensor').is_set_to(
        'sensor.some_light_switch')
    given_that.passed_arg('light_group').is_set_to(
        'light.some_controlled_lights')
    given_that.passed_arg('scene_input_select').is_set_to(
        'input_select.some_scene_input_select')
    given_that.passed_arg('scene_prefix').is_set_to(
        'Prefix')
    given_that.passed_arg('dim_step_size').is_set_to(
        'input_number.some_dim_step_size_slider')


def test_decrease_brightness_turns_on_light_group_when_off(light_switch, given_that, assert_that):
    given_that.state_of(
        'input_number.some_dim_step_size_slider').is_set_to('25.0')
    given_that.state_of('light.some_controlled_lights').is_set_to('off',
                                                                  {'entity_id': ["light.light_1",
                                                                                 "light.light_2"]})
    light_switch.increase_brightness(None, None, None, None, None)
    assert_that('light.some_controlled_lights').was.turned_on()


def test_decrease_brightness_only_turned_on_lights_get_dimmed(light_switch, given_that, assert_that):
    given_that.state_of(
        'input_number.some_dim_step_size_slider').is_set_to('25.0')
    given_that.state_of('light.some_controlled_lights').is_set_to('on',
                                                                  {'entity_id': ["light.some_turned_on_light",
                                                                                 "light.some_light_without_brightness_toggle",
                                                                                 "light.some_turned_off_light"]})
    given_that.state_of('light.some_turned_on_light').is_set_to('on',
                                                                {'brightness': "125"})
    given_that.state_of(
        'light.some_light_without_brightness_toggle').is_set_to('on')
    given_that.state_of('light.some_turned_off_light').is_set_to('off')
    light_switch.decrease_brightness(None, None, None, None, None)
    assert_that('light.some_turned_on_light').was.turned_on(brightness=100)
    assert_that('light.some_light_without_brightness_toggle').was_not.turned_on()
    assert_that('light.some_turned_off_light').was_not.turned_on()


def test_decrease_brightness_turns_off_light_when_brightness_0(light_switch, given_that, assert_that):
    given_that.state_of(
        'input_number.some_dim_step_size_slider').is_set_to('25.0')
    given_that.state_of('light.some_controlled_lights').is_set_to('on',
                                                                  {'entity_id': ["light.light_1",
                                                                                 "light.light_2"]})
    given_that.state_of('light.light_1').is_set_to('on',
                                                   {'brightness': "12"})
    given_that.state_of('light.light_2').is_set_to('on',
                                                   {'brightness': "125"})
    light_switch.decrease_brightness(None, None, None, None, None)
    assert_that('light.light_1').was.turned_off()
    assert_that('light.light_2').was.turned_on(brightness=100)


def test_increase_brightness_only_turned_on_lights_get_dimmed(light_switch, given_that, assert_that):
    given_that.state_of(
        'input_number.some_dim_step_size_slider').is_set_to('25.0')
    given_that.state_of('light.some_controlled_lights').is_set_to('on',
                                                                  {'entity_id': ["light.some_turned_on_light",
                                                                                 "light.some_light_without_brightness_toggle",
                                                                                 "light.some_turned_off_light"]})
    given_that.state_of('light.some_turned_on_light').is_set_to('on',
                                                                {'brightness': "125"})
    given_that.state_of(
        'light.some_light_without_brightness_toggle').is_set_to('on')
    given_that.state_of('light.some_turned_off_light').is_set_to('off')
    light_switch.increase_brightness(None, None, None, None, None)
    assert_that('light.some_turned_on_light').was.turned_on(brightness=150)
    assert_that('light.some_turned_off_light').was_not.turned_on()
    assert_that('light.some_light_without_brightness_toggle').was_not.turned_on()


def test_increase_brightness_only_increases_to_max_255(light_switch, given_that, assert_that):
    given_that.state_of(
        'input_number.some_dim_step_size_slider').is_set_to('25.0')
    given_that.state_of('light.some_controlled_lights').is_set_to('on',
                                                                  {'entity_id': ["light.light_1",
                                                                                 "light.light_2"]})
    given_that.state_of('light.light_1').is_set_to('on',
                                                   {'brightness': "250"})
    given_that.state_of('light.light_2').is_set_to('on',
                                                   {'brightness': "125"})
    light_switch.increase_brightness(None, None, None, None, None)
    assert_that('light.light_1').was.turned_on(brightness=255)
    assert_that('light.light_2').was.turned_on(brightness=150)


def test_increase_brightness_turns_on_light_group_when_off(light_switch, given_that, assert_that):
    given_that.state_of(
        'input_number.some_dim_step_size_slider').is_set_to('25.0')
    given_that.state_of('light.some_controlled_lights').is_set_to('off',
                                                                  {'entity_id': ["light.light_1",
                                                                                 "light.light_2"]})
    light_switch.increase_brightness(None, None, None, None, None)
    assert_that('light.some_controlled_lights').was.turned_on()


def test_toggle_light_group_is_turned_on_when_off(light_switch, given_that, assert_that):
    given_that.state_of('light.some_controlled_lights').is_set_to('off')
    light_switch.toggle_light_group(None, None, None, None, None)
    assert_that('light.some_controlled_lights').was.turned_on()


def test_toggle_light_group_is_turned_off_when_on(light_switch, given_that, assert_that):
    given_that.state_of('light.some_controlled_lights').is_set_to('on')
    light_switch.toggle_light_group(None, None, None, None, None)
    assert_that('light.some_controlled_lights').was.turned_off()


def test_switch_to_next_scene(light_switch, given_that, assert_that):
    given_that.state_of(
        'input_select.some_scene_input_select').is_set_to('Test 1')
    light_switch.switch_to_next_scene(None, None, None, None, None)
    assert_that('input_select/select_next') \
        .was.called_with(entity_id='input_select.some_scene_input_select')
    assert_that('scene/turn_on') \
        .was.called_with(entity_id='scene.prefix_test_1')


def test_switch_to_previous_scene(light_switch, given_that, assert_that):
    given_that.state_of(
        'input_select.some_scene_input_select').is_set_to('Test 1')
    light_switch.switch_to_previous_scene(None, None, None, None, None)
    assert_that('input_select/select_previous') \
        .was.called_with(entity_id='input_select.some_scene_input_select')
    assert_that('scene/turn_on') \
        .was.called_with(entity_id='scene.prefix_test_1')
