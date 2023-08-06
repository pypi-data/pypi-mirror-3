import logging
import os
import paramiko as ssh

log = logging.getLogger("charmrunner.sftp")

# Paramiko is very verbose.
ssh_log = logging.getLogger("paramiko.transport")
ssh_log.setLevel(logging.WARN)


def get_connection(host):
    client = ssh.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(ssh.AutoAddPolicy())
    client.connect(host, username="ubuntu", compress=True)
    return client


def get_files(host, files):
    conn = get_connection(host)
    sftp = conn.open_sftp()

    for l_path, r_path in files:
        log.info("Fetching %s:%s", host, r_path)
        sftp.get(r_path, l_path)

    sftp.close()
    conn.close()


def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(name)s:%(levelname)s %(message)s")

    get_files(
        "10.0.3.79",
        [
            (os.path.join(os.path.abspath('tdata'), "machine-agent.log"),
             '/var/log/juju/machine-agent.log'),
            (os.path.join(os.path.abspath('tdata'), "cloud-init.log"),
             '/var/log/cloud-init-output.log')])

if __name__ == '__main__':
    main()
