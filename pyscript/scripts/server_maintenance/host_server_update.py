from tools.ssh_shell import run_remote_apt_command


def run_update_command(command):
    std_err = task.executor(run_remote_apt_command, command,
                            pyscript.config["pyscript"]["global"]["host_server"]["ssh_login"],
                            pyscript.config["pyscript"]["global"]["host_server"]["ssh_key"],
                            pyscript.config["pyscript"]["global"]["host_server"]["ssh_sudo"])
    if std_err:
        log.error("error during excution of apt command '" +
                  command + "': " + str(std_err))
        return False
    return True


@service
def update_host_machine():
    log.info("Running host server update")
    if run_update_command("update"):
        if run_update_command("upgrade"):
            if run_update_command("dist-upgrade"):
                log.info("Host server update successfully completed")
                return
    log.error("Host server update resulted in error")
    notify.persistent_notification(
        title="Host Server Update failed", message="Errors occured during apt update on host server.")
