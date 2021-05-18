#!/usr/local/bin/python
# coding: utf8

import os
import subprocess

secrets = {}
with open("secrets.yaml") as secrets_file:
    for line in secrets_file:
        name, var = line.partition(":")[::2]
        secrets[name.strip()] = str(var).strip()

sudo_password = secrets["host_sudo"]

def run_apt_command(command_name):
    command_array = ['ssh', '-i', '.ssh/id_rsa', 'robert@rpn-home-server',
                     'echo', sudo_password, "|",  'sudo', '-S', 'apt-get', '-y']
    with open("tmp/home_server_update_log.log", "ab") as log_file:
        apt_command = command_array.copy()
        apt_command.append(command_name)
        log_file.write(
            bytes("Running: " + str(" ".join(apt_command) + "\n"), "utf-8"))
        command_result = subprocess.run(apt_command, stdout=subprocess.PIPE)
        log_file.write(command_result.stdout)
        if command_result.stderr:
            log_file.write(command_result.stderr)

run_apt_command("update")
run_apt_command("upgrade")
run_apt_command("dist-upgrade")
