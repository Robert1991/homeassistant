
def read_secrets(path_to_secrets):
    secrets = {}
    with open(path_to_secrets) as secrets_file:
        for line in secrets_file:
            name, var = line.partition(":")[::2]
            secrets[name.strip()] = str(var).strip()
    return secrets
