import argparse
import logging
import os
import zipfile

import zookeeper

from juju.environment.config import EnvironmentsConfig

log = logging.getLogger("jujitsu.zkdump")


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


def setup_parser():
    parser = argparse.ArgumentParser(
        description="Dumps environment zookeeper state to a zip")
    parser.add_argument("-f", "--archive-file", required=True,
                        help="Archive zip to record to")
    parser.add_argument("-e", "--environment",
                        help="Environment to act upon (uses default else)")
    return parser


def main():
    parser = setup_parser()
    options = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(name)s:%(levelname)s %(message)s")

    output_path = os.path.abspath(options.archive_file)

    env_config = EnvironmentsConfig()
    env_config.load_or_write_sample()
    if options.environment:
        environment = env_config.get(options.environment)
    else:
        environment = env_config.get_default()

    provider = environment.get_machine_provider()

    archive = zipfile.ZipFile(
        output_path, 'w', compression=zipfile.ZIP_DEFLATED)
    archive_zookeeper(archive, provider, prefix="zk")
    archive.close()


if __name__ == '__main__':
    main()
