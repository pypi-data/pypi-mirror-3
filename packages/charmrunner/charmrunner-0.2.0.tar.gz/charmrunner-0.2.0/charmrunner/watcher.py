"""
Given a service name, determine if that service and all of its relations
have reached a viable steady state.


  - Make sure all machines associated to units are running.
  - Make sure all units are running.
  - Check all relations.

If anything is broken, bail immediately.
"""

import argparse
import logging
import time
import sys
import zookeeper

from twisted.internet.defer import Deferred
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from twisted.python.failure import Failure

from juju.environment.config import EnvironmentsConfig
from juju.control.status import collect


log = logging.getLogger("juju.service_watch")


class ServiceWatcher(object):

    def __init__(
        self, service_name, environment, timeout, max_time, poll_interval=10):
        """
        """
        self.service_name = service_name
        self.environment = environment
        self.provider = environment.get_machine_provider()
        self.timeout = timeout
        self.poll_interval = poll_interval

        self.exit_code = 0
        self.completed = False
        self.completed_count = 0
        self.last_activity = time.time()
        self.last_status = None
        self.max_time = time.time() + max_time

        self.finished = Deferred()
        self.finished.addBoth(self.on_finish)

    @inlineCallbacks
    def __call__(self):
        try:
            self.client = yield self.provider.connect()
            self.setup_poll()
            self.exit_code = yield self.finished
        finally:
            reactor.stop()

    def on_finish(self, result):
        """ Called on exit from the service watcher.
        """
        log.info("Finished")
        exit_code = 0
        if isinstance(result, Failure):
            log.error(result.getErrorMessage())
            print >> sys.stderr, result.getErrorMessage()
            exit_code = 1
        return exit_code

    def setup_poll(self):

        @inlineCallbacks
        def _poll():
            yield self.poll()
            if self.finished.called:
                return
            else:
                reactor.callLater(self.poll_interval, _poll)

        reactor.callLater(self.poll_interval, _poll)

    def check_time(self, state):
        current_time = time.time()

        # Check if we've already completed
        if self.completed:
            #max_count = int((self.timeout / self.poll_interval))
            if self.completed_count > 10:
                self.finished.callback("Success")
            else:
                self.completed_count += 1
        # Make sure we haven't reached our max time
        if (current_time > self.max_time):
            self.finished.errback(ValueError("max time out reached"))
        # Check that we haven't passed our activity timeout
        elif state == self.last_status and \
               (self.timeout + self.last_activity) < current_time:
            if self.completed:
                self.finished.callback("Success")
            else:
                self.finished.errback(ValueError("activity timeout reached"))
        # Verify that the service is indeed part of the environment
        elif not self.service_name in state['services']:
            self.finished.errback(ValueError(
                "service %s is not in environment" % self.service_name))
        else:
            self.last_status = state
            if state != self.last_status:
                self.last_activity = time.time()
            return False
        return True

    @inlineCallbacks
    def poll(self):
        log.debug("polling")
        state = yield collect(None, self.provider, self.client, log)

        # Verify time invariants
        if self.check_time(state):
            return

        # Check machines, units, and relations
        service_info = state['services'][self.service_name]
        relations = service_info["relations"]

        for unit_id, unit_info in service_info['units'].items():
            machine_id = unit_info['machine']
            machine_info = state['machines'][machine_id]

            for label, value in (
                ('machine %s' % machine_id, machine_info['state']),
                ('machine %s' % machine_id, machine_info['instance-state']),
                ('unit %s' % unit_id, unit_info['state'])):

                if not value in ("running",
                                 "pending",
                                 "installed",
                                 "not-started",
                                 "started"):
                    self.finished.errback(("%s startup failed %s" % (
                        label, value)))

                if value in ("pending", "not-started"):
                    return

            for relation_id, relation_info in unit_info['relations'].items():
                if relation_info['state'] != 'up':
                    self.finished.errback(
                        ValueError("%s relation failed %s %s" % (
                            relation_info, relations[relation_id])))
                    return

        log.debug("service complete")
        self.completed = True
        self.completed_count += 1


def setup_parser():
    parser = argparse.ArgumentParser(
        description="Watch for services and relations to come up")
    parser.add_argument("service", default=False,
                        help="Service to watch")

    parser.add_argument(
        "-p", "--poll-interval", default=3,
        help="Time(s) between status polls")

    #parser.add_argument(
    #    "-i", "--inactive-count", default=10,
    #    help="Number of polls without activity, before considered stable")

    parser.add_argument(
        "-a", "--activity-timeout", default=30,
        help="Number of seconds without activity, before considered stable")

    # Maximum allotted is 10m
    parser.add_argument(
        "-m", "--max-time", default=600,
        help="Maximum time allotted for test")

    return parser


def main():
    parser = setup_parser()
    options = parser.parse_args()
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(name)s:%(levelname)s %(message)s")

    zookeeper.set_debug_level(0)
    env_config = EnvironmentsConfig()
    env_config.load_or_write_sample()
    environment = env_config.get_default()

    watcher = ServiceWatcher(
        options.service,
        environment,
        timeout=options.activity_timeout,
        max_time=options.max_time,
        poll_interval=options.poll_interval)

    reactor.callWhenRunning(watcher)
    reactor.run()
    sys.exit(watcher.exit_code)


if __name__ == '__main__':
    main()
