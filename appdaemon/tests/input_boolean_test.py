from apps.general.input_boolean import ReactivationTimer

import pytest
from appdaemontestframework import automation_fixture


@automation_fixture(ReactivationTimer)
def reactivation_timer(given_that):
    given_that.passed_arg('observed_input_boolean').is_set_to(
        'input_boolean.some_observed_bool')
    given_that.passed_arg('reactivation_timeout').is_set_to(
        'input_datetime.light_automation_reactivation_timeout')


def test_start_timer_input_boolean_is_turned_on_when_timer_elapsed(given_that, reactivation_timer, assert_that, time_travel):
    given_that.state_of(
        'input_datetime.light_automation_reactivation_timeout').is_set_to('01:30:59')
    reactivation_timer.start_timer(None, None, None, None, None)
    time_travel.fast_forward(45).minutes()
    assert_that('input_boolean.some_observed_bool').was_not.turned_on()
    time_travel.fast_forward(46).minutes()
    assert_that('input_boolean.some_observed_bool').was.turned_on()


def test_start_timer_timer_is_cancelled_when_input_boolean_on_again(given_that, reactivation_timer, assert_that, time_travel):
    given_that.state_of(
        'input_datetime.light_automation_reactivation_timeout').is_set_to('01:30:59')
    reactivation_timer.start_timer(None, None, None, None, None)
    time_travel.fast_forward(45).minutes()
    reactivation_timer.stop_timer(None, None, None, None, None)
    time_travel.fast_forward(46).minutes()
    assert_that('input_boolean.some_observed_bool').was_not.turned_on()
