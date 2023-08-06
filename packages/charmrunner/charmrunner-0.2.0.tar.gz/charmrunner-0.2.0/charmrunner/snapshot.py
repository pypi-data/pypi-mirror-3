import argparse
import logging
import os
import json
import subprocess
import sys
import zookeeper

from env import status, destroy

log = logging.getLogger("juijtsu.snapshot")


def clean_juju_state(deleted_services):
    from twisted.internet import reactor
    from twisted.internet.defer import inlineCallbacks
    from juju.environment.config import EnvironmentsConfig
    from juju.state.service import ServiceStateManager

    env_config = EnvironmentsConfig()
    env_config.load_or_write_sample()
    environment = env_config.get_default()

    @inlineCallbacks
    def _clean_juju_state():
        zookeeper.set_debug_level(0)
        provider = environment.get_machine_provider()
        storage = provider.get_file_storage()

        client = yield provider.connect()
        charms = yield client.get_children("/charms")

        # Delete any cached charm state in zookeeper
        deleted_charms = []

        for s in deleted_services:  # XXX fuzzy match..
            for c in charms:
                if s in c:
                    deleted_charms.append(c)
        for s in (yield ServiceStateManager(client).get_all_service_states()):
            charm_id = yield s.get_charm_id()
            if charm_id in deleted_charms:
                deleted_charms.remove(charm_id)

        log.debug("Removing charms %r" % deleted_charms)
        for d in deleted_charms:
            yield client.delete("/charms/%s" % d)

        # Clear out any cached charm state in the local provider storage.
        for f in list(os.listdir(storage._path)):
            for s in deleted_services:
                if s in f:
                    os.remove(os.path.join(storage._path, f))

        reactor.stop()

    reactor.callWhenRunning(_clean_juju_state)
    reactor.run()


class EnvironmentSnapshot(object):

    def __init__(self, state_file_path):
        self.state_file_path = state_file_path

    @property
    def _state_path(self):
        return self.state_file_path

    def restore(self):
        with open(self._state_path) as fh:
            previous = json.loads(fh.read())

        current = status()

        current = current['services'].keys()
        previous = previous['services'].keys()
        added = set(current) - set(previous)

        log.info("Restoring environment (deleting %s services)", len(added))
        log.debug("Deleted services %s" % list(added))

        for a in added:
            destroy(a)

        # Still need to clear out the charms from zk
        clean_juju_state(added)

    def save(self):
        state = status()
        log.info(
            "Snapshotting environment (%d services)", len(state['services']))
        with open(self._state_path, "w") as fh:
            fh.write(json.dumps(state, indent=2))


def setup_parser():
    parser = argparse.ArgumentParser(description="Snapshot an environment")
    parser.add_argument("subcommand", nargs="?",
                        choices=('restore', 'snapshot'),
                        default='snapsphot',
                        help="Action to perform (Default snapshot)")
    parser.add_argument("-f", "--state-file", required=True,
                        help="State file for environment snapshot")
    parser.add_argument("-v", "--verbose", action="store_true", default=False,
                        help="Log level for operations")
    return parser


def main():
    options = setup_parser().parse_args()

    log_options = {
        "level": logging.DEBUG,
        "format": "%(asctime)s %(name)s:%(levelname)s %(message)s"}
    logging.basicConfig(**log_options)

    # Verify state path:
    options.state_file = os.path.abspath(options.state_file)

    # Verify environment
    try:
        status(with_stderr=True)
    except subprocess.CalledProcessError, e:
        log.error("Environment not available\n%s\n%s" % (
            " ".join(e.cmd), e.output))
        sys.exit(1)

    snapshot = EnvironmentSnapshot(options.state_file)

    if options.subcommand == 'snapshot':
        snapshot.save()
    elif options.subcommand == 'restore':
        if not os.path.exists(options.state_file):
            log.warning("Invalid state path %s" % options.state_file)
            return sys.exit(1)
        snapshot.restore()
        log.info("Restoration complete")


if __name__ == '__main__':
    main()
