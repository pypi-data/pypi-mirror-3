"""
Juju environment recorder.

 - Captures all logs
 - Captures zookeeper state.

"""
import argparse
import json
import logging
import os
import tempfile
import zipfile
import zookeeper

from juju.control.utils import get_environment
from juju.environment.config import EnvironmentsConfig

from env import status
from sftp import get_files

log = logging.getLogger("jujitsu.recorder")


def setup_parser():
    parser = argparse.ArgumentParser(
        description="Gather logs and records for an environment")
    parser.add_argument("-e", "--environment",
                        help="Environment to operate on")
    parser.add_argument("-f", "--archive-file", required=True,
                        help="Archive zip to record to")
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


def archive_logs(archive, provider, svc_data):
    log.info("Capturing logs")
    store_dir = tempfile.mkdtemp()
    host_files = group_files_by_host(
        svc_data, store_dir, provider.provider_type)
    for host, files in host_files.items():
        get_files(host, files)
    for f_path in os.listdir(store_dir):
        archive.write(
            os.path.join(store_dir, f_path), arcname="logs/%s" % f_path)


def group_files_by_host(svc_data, store_dir, provider_type):
    # Group files to retrieve by host
    host_files = {}

    # Get unit logs
    for service_name, service_info in svc_data['services'].items():
        for unit_name, unit_info in service_info['units'].items():
            unit_fs_id = unit_name.replace("/", "-")
            if provider_type == "local":
                r_unit_log_path = os.path.join(
                    "/var/log/juju/unit-%s.log" % unit_fs_id)
            else:
                r_unit_log_path = os.path.join(
                    "/var/lib/juju/units/%s/charm.log" % unit_fs_id)

            host_files.setdefault(unit_info['public-address'], []).append((
                os.path.join(store_dir, "unit-%s.log" % unit_fs_id),
                r_unit_log_path))

    # Get machine logs
    for machine_id, machine in svc_data['machines'].items():
        if not machine.get('dns-name'):
            continue
        host_files.setdefault(machine['dns-name'], []).append((
            os.path.join(store_dir, "machine-%s.log" % machine_id),
            "/var/log/juju/machine-agent.log"
            ))

    # Provisioning agent logs
    if provider_type != 'local':
        host_files.setdefault(
            svc_data['machines']['0']['dns-name'], []).append((
            os.path.join(store_dir, "provisioning-agent.log"),
            "/var/log/juju/provision-agent.log"
            ))

    return host_files


def main():
    parser = setup_parser()
    options = parser.parse_args()
    options.environments = EnvironmentsConfig()
    options.environments.load_or_write_sample()

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(name)s:%(levelname)s %(message)s")

    log.info("hello")
    print "hello 2"
    output_path = os.path.abspath(options.archive_file)

    environment = get_environment(options)
    provider = environment.get_machine_provider()

    svc_data = status(options.environment)

    archive = zipfile.ZipFile(
        output_path, 'w', compression=zipfile.ZIP_DEFLATED)
    archive.writestr("status.json", json.dumps(svc_data, indent=2))

    archive_logs(archive, provider, svc_data)
    archive_zookeeper(archive, provider, prefix="zk")
    archive.close()


if __name__ == '__main__':
    try:
        main()
    except:
        import pdb, traceback, sys
        traceback.print_exc()
        pdb.post_mortem(sys.exc_info()[-1])
