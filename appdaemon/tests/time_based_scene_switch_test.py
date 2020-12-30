from apps.lights.time_based_scene_switch import TimeBasedSceneSwitch

import pytest
from appdaemontestframework import automation_fixture
from datetime import time
import mock
from mock import patch


@automation_fixture(TimeBasedSceneSwitch)
def scene_switch(given_that):
    given_that.passed_arg('scene_switch_input_select')  \
        .is_set_to('input_select.some_time_based_scenes')
    given_that.passed_arg('toggled_scene_input_select') \
        .is_set_to('input_select.some_scene_toggle_input_select')
    given_that.passed_arg('light_automatic_enabled') \
        .is_set_to('input_boolean.some_light_automatic_switch')


def test_refresh_listeners_check_that_scene_switch_timer_are_set_check_current_scene_activated(given_that, scene_switch, assert_that, time_travel):
    given_that.time_is(time(hour=20))
    given_that.state_of('input_datetime.work_light_start_time') \
        .is_set_to('08:30:00')
    given_that.state_of('input_select.work_light_input_select') \
        .is_set_to('Work Light')
    given_that.state_of('input_datetime.night_light_start_time') \
        .is_set_to('22:45:00')
    given_that.state_of('input_select.night_light_input_select') \
        .is_set_to('Night Light')
    given_that.state_of('input_select.some_time_based_scenes') \
        .is_set_to('work_light_start_time/Work Light',
                   {'options': ['work_light_start_time/work_light_input_select',
                                'night_light_start_time/night_light_input_select']})

    with patch('appdaemon.plugins.hass.hassapi.Hass.select_option') as mock:
        scene_switch.refresh_listeners(None, None, None, None, None)

    assert_that(scene_switch) \
        .registered.run_daily(time(hour=8, minute=30), scene="Work Light") \
        .with_callback(scene_switch.toggle_scene)
    assert_that(scene_switch) \
        .listens_to.state("input_datetime.work_light_start_time") \
        .with_callback(scene_switch.refresh_listeners)
    assert_that(scene_switch) \
        .listens_to.state("input_select.work_light_input_select") \
        .with_callback(scene_switch.refresh_listeners)
    assert_that(scene_switch) \
        .registered.run_daily(time(hour=22, minute=45), scene="Night Light") \
        .with_callback(scene_switch.toggle_scene)
    assert_that(scene_switch) \
        .listens_to.state("input_datetime.night_light_start_time") \
        .with_callback(scene_switch.refresh_listeners)
    assert_that(scene_switch) \
        .listens_to.state("input_select.night_light_input_select") \
        .with_callback(scene_switch.refresh_listeners)
    mock.assert_called_with(
        "input_select.some_scene_toggle_input_select", "Work Light")


def test_refresh_listeners_check_that_scene_switch_timer_are_set_check_current_scene_activated_during_night(given_that, scene_switch, assert_that, time_travel):
    given_that.time_is(time(hour=1))
    given_that.state_of('input_datetime.work_light_start_time') \
        .is_set_to('08:30:00')
    given_that.state_of('input_select.work_light_input_select') \
        .is_set_to('Work Light')
    given_that.state_of('input_datetime.night_light_start_time') \
        .is_set_to('22:45:00')
    given_that.state_of('input_select.night_light_input_select') \
        .is_set_to('Night Light')
    given_that.state_of('input_select.some_time_based_scenes') \
        .is_set_to('work_light_start_time/work_light_input_select',
                   {'options': ['night_light_start_time/night_light_input_select',
                                'work_light_start_time/work_light_input_select']})

    with patch('appdaemon.plugins.hass.hassapi.Hass.select_option') as mock:
        scene_switch.refresh_listeners(None, None, None, None, None)

    assert_that(scene_switch) \
        .registered.run_daily(time(hour=8, minute=30), scene="Work Light") \
        .with_callback(scene_switch.toggle_scene)
    assert_that(scene_switch) \
        .listens_to.state("input_datetime.work_light_start_time") \
        .with_callback(scene_switch.refresh_listeners)
    assert_that(scene_switch) \
        .listens_to.state("input_select.work_light_input_select") \
        .with_callback(scene_switch.refresh_listeners)
    assert_that(scene_switch) \
        .registered.run_daily(time(hour=22, minute=45), scene="Night Light") \
        .with_callback(scene_switch.toggle_scene)
    assert_that(scene_switch) \
        .listens_to.state("input_datetime.night_light_start_time") \
        .with_callback(scene_switch.refresh_listeners)
    assert_that(scene_switch) \
        .listens_to.state("input_select.night_light_input_select") \
        .with_callback(scene_switch.refresh_listeners)
    mock.assert_called_with(
        "input_select.some_scene_toggle_input_select", "Night Light")


def test_refresh_listeners_listeners_updated_on_next_call(given_that, scene_switch, assert_that, time_travel):
    given_that.time_is(time(hour=8))

    given_that.state_of('input_select.some_time_based_scenes') \
        .is_set_to('work_light_start_time/work_light_input_select',
                   {'options': ['work_light_start_time/work_light_input_select']})
    given_that.state_of('input_datetime.work_light_start_time') \
        .is_set_to('08:30:00')
    given_that.state_of('input_select.work_light_input_select') \
        .is_set_to('Work Light')

    with patch('appdaemon.plugins.hass.hassapi.Hass.select_option') as mock:
        scene_switch.refresh_listeners(None, None, None, None, None)

    assert_that(scene_switch) \
        .listens_to.state("input_datetime.work_light_start_time") \
        .with_callback(scene_switch.refresh_listeners)
    assert_that(scene_switch) \
        .listens_to.state("input_select.work_light_input_select") \
        .with_callback(scene_switch.refresh_listeners)
    mock.assert_called_with(
        "input_select.some_scene_toggle_input_select", "Work Light")

    given_that.mock_functions_are_cleared()
    given_that.state_of('input_select.some_time_based_scenes') \
        .is_set_to('night_light_start_time/night_light_input_select',
                   {'options': ['night_light_start_time/night_light_input_select']})
    given_that.state_of('input_datetime.night_light_start_time') \
        .is_set_to('10:30:00')
    given_that.state_of('input_select.night_light_input_select') \
        .is_set_to('Night Light')

    with patch('appdaemon.plugins.hass.hassapi.Hass.select_option') as select_option_mock:
        with patch('appdaemon.plugins.hass.hassapi.Hass.cancel_listen_state'):
            scene_switch.refresh_listeners(None, None, None, None, None)

    assert_that(scene_switch) \
        .registered.run_daily(time(hour=10, minute=30), scene="Night Light") \
        .with_callback(scene_switch.toggle_scene)
    select_option_mock.assert_called_with(
        "input_select.some_scene_toggle_input_select", "Night Light")
    assert_that(scene_switch) \
        .listens_to.state("input_datetime.night_light_start_time") \
        .with_callback(scene_switch.refresh_listeners)
    assert_that(scene_switch) \
        .listens_to.state("input_select.night_light_input_select") \
        .with_callback(scene_switch.refresh_listeners)
    with pytest.raises(AssertionError):
        assert_that(scene_switch) \
            .listens_to.state("input_datetime.work_light_start_time") \
            .with_callback(scene_switch.refresh_listeners)
        assert_that(scene_switch) \
            .listens_to.state("input_select.work_light_input_select") \
            .with_callback(scene_switch.refresh_listeners)
        assert_that(scene_switch) \
            .registered.run_daily(time(hour=8, minute=30), scene="Work Light") \
            .with_callback(scene_switch.toggle_scene)


def test_refresh_listeners_not_registered_when_input_select_entry_malformed(given_that, scene_switch, assert_that, time_travel):
    given_that.state_of('input_datetime.work_light_start_time') \
        .is_set_to('08:30:00')
    given_that.state_of('input_select.some_time_based_scenes') \
        .is_set_to('work_light_start_time/Work Light',
                   {'options': ['work_light_start_time_Work Light']})
    scene_switch.refresh_listeners(None, None, None, None, None)
    with pytest.raises(AssertionError):
        assert_that(scene_switch) \
            .registered.run_daily(time(hour=8, minute=30), scene="Work Light") \
            .with_callback(scene_switch.toggle_scene)


def test_toggle_scene(given_that, scene_switch, assert_that, time_travel):
    with patch('appdaemon.plugins.hass.hassapi.Hass.select_option') as mock:
        scene_switch.toggle_scene({"scene": "Scene Name"})
    mock.assert_called_with(
        "input_select.some_scene_toggle_input_select", "Scene Name")
