from apps.lights.light_control import DimLights
from appdaemon.plugins.hass.hassapi import Hass
from mock import patch, MagicMock
import pytest

from appdaemontestframework import automation_fixture


@automation_fixture(DimLights)
def dim_lights(given_that):
    given_that.passed_arg('light_group').is_set_to('group.some_light_group')
    given_that.passed_arg('light_sensor').is_set_to(
        'sensor.light_intensity_in_percent')
    given_that.passed_arg('light_threshold').is_set_to(
        'input_number.some_input_slider')


def test_toggle_event_when_light_group_is_off(given_that, dim_lights, assert_that):
    given_that.state_of('group.some_light_group').is_set_to('off')
    dim_lights.toggle_event(
        'input_number.some_input_slider', None, None, None, None)
    assert_that('light.some_light').was_not.turned_on()


def test_toggle_event_when_current_light_greater_than_threshold(given_that, dim_lights, assert_that):
    given_that.state_of("light.some_light").is_set_to("on")
    given_that.state_of('group.some_light_group').is_set_to('on',
                                                            {'entity_id': ["light.some_light"]})
    given_that.state_of('sensor.light_intensity_in_percent').is_set_to('70.0')
    given_that.state_of('input_number.some_input_slider').is_set_to('80.0')
    dim_lights.toggle_event(
        'group.some_light_group', None, None, None, None)
    assert_that('light.some_light').was_not.turned_on()
