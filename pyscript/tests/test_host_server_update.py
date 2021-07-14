from ..modules.testtools.function_decorators import pyscript_compile
from ..modules.testtools.function_decorators import service
from ..modules.testtools.context_tools import load_file_to_global_context_without_imports
from unittest.mock import patch
from unittest.mock import MagicMock
from unittest.mock import call
import pytest


@pytest.fixture(autouse=True)
def host_server_update_setup():
    load_file_to_global_context_without_imports(
        "../scripts/server_maintenance/host_server_update.py", globals(),
        ["log", "task", "notify", "pyscript", "run_remote_apt_command"])
    pyscript.config = {
        "pyscript": {
            "global": {
                "host_server": {
                    "ssh_login": "foo@server",
                    "ssh_key": ".ssh/id_rsa",
                    "ssh_sudo": "sudo!"
                }}}}


def test_update_host_machine_apt_command_invocation():
    task.executor = MagicMock(return_value=None)

    update_host_machine()

    executor_calls = [call(run_remote_apt_command,  'update',
                           'foo@server', '.ssh/id_rsa', 'sudo!'),
                      call(run_remote_apt_command,  'upgrade',
                           'foo@server', '.ssh/id_rsa', 'sudo!'),
                      call(run_remote_apt_command, 'dist-upgrade',
                           'foo@server', '.ssh/id_rsa', 'sudo!')]
    task.executor.assert_has_calls(executor_calls)

    log_calls = [call("Running host server update"),
                 call("Host server update successfully completed")]
    log.info.assert_has_calls(log_calls)
    assert notify.called == False


def test_update_host_machine_apt_command_invocation_with_error_upgrade():
    task.executor = MagicMock(side_effect=[None, "error"])

    update_host_machine()

    executor_calls = [call(run_remote_apt_command,  'update',
                           'foo@server', '.ssh/id_rsa', 'sudo!'),
                      call(run_remote_apt_command,  'upgrade',
                           'foo@server', '.ssh/id_rsa', 'sudo!')]
    task.executor.assert_has_calls(executor_calls)
    log.info.assert_called_once_with("Running host server update")

    error_log = [
        call("error during excution of apt command 'upgrade': error"),
        call("Host server update resulted in error")]
    log.error.assert_has_calls(error_log)
    notify.persistent_notification.assert_called_once_with(
        title="Host Server Update failed", message="Errors occured during apt update on host server.")


def test_update_host_machine_apt_command_invocation_with_error_update():
    task.executor = MagicMock(side_effect=["error"])

    update_host_machine()

    task.executor.assert_called_once_with(run_remote_apt_command,  'update',
                                          'foo@server', '.ssh/id_rsa', 'sudo!')
    log.info.assert_called_once_with("Running host server update")

    error_log = [
        call("error during excution of apt command 'update': error"),
        call("Host server update resulted in error")]
    log.error.assert_has_calls(error_log)
    notify.persistent_notification.assert_called_once_with(
        title="Host Server Update failed", message="Errors occured during apt update on host server.")


def test_update_host_machine_apt_command_invocation_with_error_dist_upgrade():
    task.executor = MagicMock(side_effect=[None, None, "error"])

    update_host_machine()

    executor_calls = [call(run_remote_apt_command,  'update',
                           'foo@server', '.ssh/id_rsa', 'sudo!'),
                      call(run_remote_apt_command,  'upgrade',
                           'foo@server', '.ssh/id_rsa', 'sudo!'),
                      call(run_remote_apt_command,  'dist-upgrade',
                           'foo@server', '.ssh/id_rsa', 'sudo!')]
    task.executor.assert_has_calls(executor_calls)
    log.info.assert_called_once_with("Running host server update")

    error_log = [
        call("error during excution of apt command 'dist-upgrade': error"),
        call("Host server update resulted in error")]
    log.error.assert_has_calls(error_log)
    notify.persistent_notification.assert_called_once_with(
        title="Host Server Update failed", message="Errors occured during apt update on host server.")
