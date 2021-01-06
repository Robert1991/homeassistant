from apps.button.button_handler import ButtonEventHub
from mock import patch
from mock import call
import pytest
import datetime
from appdaemontestframework import automation_fixture


@automation_fixture(ButtonEventHub)
def event_hub(given_that):
    given_that.passed_arg("observed_button").is_set_to("sensor.some_button")
    given_that.passed_arg("button_press_timeout").is_set_to(10)
    given_that.time_is(datetime.time(hour=20))

def test_press_event_raised_when_button_release_occurs_before_timeout(event_hub, given_that, assert_that):
    with patch('appdaemon.plugins.hass.hassapi.Hass.fire_event') as mock:
        with patch('appdaemon.plugins.hass.hassapi.Hass.get_now_ts', side_effect=[10.0, 15.0]):
            event_hub.pressed_button_event(None, None, None, None, None)
            event_hub.released_button_event(None, None, None, None, None)
            mock.assert_called_with("sensor.some_button" + "_" + "press")

def test_release_event_raised_when_button_release_occurs_after_timeout(event_hub, given_that, assert_that):
    with patch('appdaemon.plugins.hass.hassapi.Hass.fire_event') as mock:
        with patch('appdaemon.plugins.hass.hassapi.Hass.get_now_ts', side_effect=[10.0, 21.0]):
            event_hub.pressed_button_event(None, None, None, None, None)
            event_hub.released_button_event(None, None, None, None, None)
            mock.assert_called_with("sensor.some_button" + "_" + "release")

def test_hold_events_raised_when_occured_before_release(event_hub, given_that, assert_that):
    with patch('appdaemon.plugins.hass.hassapi.Hass.fire_event') as mock:
        with patch('appdaemon.plugins.hass.hassapi.Hass.get_now_ts', side_effect=[10.0, 15.0, 19.0, 21.0]):
            event_hub.pressed_button_event(None, None, None, None, None)
            event_hub.hold_button_event(None, None, None, None, None)
            event_hub.hold_button_event(None, None, None, None, None)
            event_hub.released_button_event(None, None, None, None, None)

            calls = [call("sensor.some_button_hold"), \
                     call("sensor.some_button_hold"), \
                     call("sensor.some_button_end_hold") ]
            mock.has_calls(calls)

