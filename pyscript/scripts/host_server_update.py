import subprocess


@pyscript_compile
def run_apt_command(command_name, login, password):
    command_array = ['ssh', '-i', '.ssh/id_rsa', login,
                     'echo', password, "|",  'sudo', '-S', 'apt-get', '-y']
    with open("tmp/home_server_update_log.log", "ab") as log_file:
        apt_command = command_array.copy()
        apt_command.append(command_name)
        command_result = subprocess.run(apt_command, stdout=subprocess.PIPE)
        log_file.write(command_result.stdout)
        if command_result.stderr:
            log_file.error("error occured during execution of apt" +
                           command_name + ": " + command_result.stderr)
            return command_result.stderr
    return None


def run_update_command(command, host_login, host_password):
    std_err = task.executor(run_apt_command, command,
                            host_login, host_password)
    if std_err:
        log.error(std_err)
        return False
    return True


@service
def update_host_machine(host_login, host_password):
    log.info("Running host server update")
    if run_update_command("update", host_login, host_password):
        if run_update_command("upgrade", host_login, host_password):
            if run_update_command("dist-upgrade", host_login, host_password):
                log.info("Host server update successfully complteted")
                return
    log.error("Host server resulted in error")
