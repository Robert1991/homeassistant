from tools.ssh_shell import run_remote_shell_command


@service
def run_home_assistant_docker_compose_command(command=""):
    docker_compose_path = pyscript.config["global"]["host_server"]["home_assistant_docker_compose"]
    pyscript.run_docker_compose_command(
        command=command, docker_compose_path=docker_compose_path)


@service
def run_server_monitoring_docker_compose_command(command=""):
    docker_compose_path = pyscript.config["global"]["host_server"]["server_monitoring_docker_compose"]
    pyscript.run_docker_compose_command(
        command=command, docker_compose_path=docker_compose_path)


@service
def run_docker_compose_command(command="", docker_compose_path=""):
    docker_compose_command = "docker-compose -f " + \
        docker_compose_path + " " + command
    log.info("Running docker compose command: " + docker_compose_command)
    command_result = task.executor(
        run_remote_shell_command,
        docker_compose_command,
        pyscript.config["global"]["host_server"]["ssh_login"],
        pyscript.config["global"]["host_server"]["ssh_key"])
    if command_result.returncode != 0:
        log.error("Docker compose command: " +
                  docker_compose_command + " failed:\\n" + str(command_result.stderr))
        notify.persistent_notification(title="Executing Docker Compose Command Failed", message="Executing " +
                                       docker_compose_command + " failed. Check logs for more information.")
    else:
        notify.persistent_notification(title="Executing Docker Compose Command", message="Executing " +
                                       docker_compose_command + " was successful.")
        log.info("Docker compose command " +
                 docker_compose_command + " was successful")
