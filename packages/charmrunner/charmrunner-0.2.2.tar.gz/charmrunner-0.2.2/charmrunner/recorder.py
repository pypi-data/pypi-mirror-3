"""
Juju error reporter.


This cheats horribly and just assumes a local environment with
passwordless sudo
"""
import argparse
import json
import logging
import os
import subprocess
import zipfile
import zookeeper

from juju.environment.config import EnvironmentsConfig

from env import status

log = logging.getLogger("jujitsu.recorder")


def setup_parser():
    parser = argparse.ArgumentParser(
        description="Gather logs and records for an environment")
    parser.add_argument("-f", "--archive-file", required=True,
                        help="Archive zip to record to")
    parser.add_argument("-d", "--data-dir",
                        help="Additional directory to add to archive")
    return parser


def archive_zookeeper(archive, provider, prefix):
    log.info("Capturing zookeeper data")
    from twisted.internet import reactor
    from twisted.internet.defer import inlineCallbacks

    @inlineCallbacks
    def _dump(c, p):
        for child in (yield c.get_children(p)):
            if child == 'zookeeper':  # skip the md node
                continue
            child_path = "/" + ("%s/%s" % (p, child)).strip("/")
            yield _dump(c, child_path)
            contents, stat = yield c.get(child_path)
            archive.writestr(
                prefix + "/" + child_path[1:] + ".yaml", contents)

    @inlineCallbacks
    def _dump_zookeeper():
        zookeeper.set_debug_level(0)
        client = yield provider.connect()
        try:
            yield _dump(client, "/")
        finally:
            reactor.stop()

    reactor.callWhenRunning(_dump_zookeeper)
    reactor.run()


def archive_data_dir(archive, data_dir):
    log.info("Capturing data-dir %s" % data_dir)
    data_dir = os.path.abspath(data_dir)
    prefix = os.path.basename(data_dir)

    for (dir, dirs, files) in os.walk(data_dir):
        for f in files:
            p = os.path.join(dir, f)
            archive.write(p, prefix + "/" + p[len(data_dir) + 1:])


def archive_unit_logs(archive, provider, svc_data):
    log.info("Capturing unit logs")
    data_dir = provider._directory

    for service_name, service_info in svc_data['services'].items():
        for unit_name, unit_info in service_info['units'].items():
            unit_fs_id = unit_name.replace("/", "-")
            unit_dir = os.path.join(data_dir, "units", unit_fs_id)

            console_path = os.path.join(
                data_dir, "units", unit_fs_id, "container.log")
            unit_log_path = os.path.join(
                data_dir, "units", unit_fs_id, "unit.log")
            agent_log_path = os.path.join(
                data_dir, "units", unit_fs_id, "agent.log")

            subprocess.check_output(
                ["sudo", "chmod", "755", os.path.join(data_dir, "units")],
                stderr=subprocess.STDOUT)
            subprocess.check_output(
                ["sudo", "chmod", "755", unit_dir], stderr=subprocess.STDOUT)
            subprocess.check_output(
                ["sudo", "chmod", "644", console_path])
            subprocess.check_output(
                ["sudo", "cp", unit_log_path, agent_log_path])
            subprocess.check_output(
                ["sudo", "chmod", "644", agent_log_path])

            archive.write(
                console_path, arcname="units/%s/console.log" % unit_fs_id)
            archive.write(
                agent_log_path, arcname="units/%s/unit.log" % unit_fs_id)
            log.debug("Captured %s" % unit_name)


def main():
    parser = setup_parser()
    options = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(name)s:%(levelname)s %(message)s")

    output_path = os.path.abspath(options.archive_file)

    env_config = EnvironmentsConfig()
    env_config.load_or_write_sample()
    environment = env_config.get_default()
    provider = environment.get_machine_provider()

    assert environment.type == "local", \
           "Error reporting only for local environments"

    svc_data = status()

    archive = zipfile.ZipFile(
        output_path, 'w', compression=zipfile.ZIP_DEFLATED)
    archive.writestr("status.json", json.dumps(svc_data, indent=2))
    archive_unit_logs(archive, provider, svc_data)
    if options.data_dir:
        archive_data_dir(archive, options.data_dir)
    archive_zookeeper(archive, provider, prefix="zk")
    archive.close()


if __name__ == '__main__':
    main()
