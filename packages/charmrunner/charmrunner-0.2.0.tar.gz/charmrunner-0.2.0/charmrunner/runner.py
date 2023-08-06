"""
Distributed charm test runner, polls job queue, runs tests, and posts results.
"""

import argparse
import json
import logging
import os
import requests
import shutil
import subprocess
import sys

from time import sleep, time
from os.path import join

from env import is_bootstrapped

log = logging.getLogger("charmrunner")

########################################
# Distributed Test Queue Worker support.


def get_runner_environment():
    env = {}
    for x in open("/etc/lsb-release", "r"):
        k, v = x.split("=")
        v = v.strip()
        if k == 'DISTRIB_CODENAME':
            env['distro_release'] = v
        elif k == "DISTRIB_ID":
            env['distro'] = v
    osystem, hostname, kernel, tag, arch = os.uname()
    env["hostname"] = hostname
    env["kernel"] = kernel
    env["arch"] = arch
    return json.dumps(env)


def register(queue_url, otp):
    log.info("registering charmrunner")
    data = {"secret": otp}
    data["info"] = get_runner_environment()
    r = requests.post(queue_url + "register", data=data)
    if r.status_code != 200:
        raise ValueError("Error while registering\n\n %s" % r.content)
    data = json.loads(r.content)
    return data["access_token"]


def poll(queue_url, token):
    log.info("polling job")
    r = requests.post(queue_url + "next", data={"token": token})
    if not r.status_code != "200":
        log.warning(
            "Error fetching next job %s\n\n" % (r.status_code, r.content))
    data = json.loads(r.content)
    return data


def post_result(queue_url, token, job, result):
    log.info("posting results")
    if 'datafile_path' in result:
        files = {"testrecord": open(result['record'], "r")}
    else:
        files = None
    r = requests.post(
        queue_url + "results",
        data={"token": token, "result": json.dumps(result)},
        files=files)
    if r.status_code != 200:
        raise ValueError("Error while posting job results")


#########################################
# Charmrunner facade with log collection

def check():
    log.info("verifying environment running")
    if not is_bootstrapped():
        raise ValueError("Environment not bootstrapped")


def plan(repo_dir, work_dir, charm, series):
    log.info("generating test plans")
    plan_dir = join(work_dir, "plans")
    if not os.path.exists(plan_dir):
        os.mkdir(plan_dir)
    subprocess.check_call(
        ["juju-plan", "--repo", repo_dir, "-s", series, "-d", plan_dir, charm],
        stdout=open(join(work_dir, "runner", "planner.log"), "w"),
        stderr=subprocess.STDOUT)

    for p in os.listdir(plan_dir):
        yield json.load(open(join(plan_dir, p), "r"))


def load(work_dir, job):
    log.info("loading test")
    test_plan_path = join(work_dir, "runner", "test.plan")
    with open(test_plan_path, "w") as fh:
        fh.write(json.dumps(job))
    subprocess.check_call(
        ["juju-load-plan", "--reset-repo", "-r", join(work_dir, "repo"),
         test_plan_path],
        stdout=open(join(work_dir, "runner", "loader.log"), "w"),
        stderr=subprocess.STDOUT)


def snapshot(work_dir):
    log.info("snapshotting environment")
    subprocess.check_call(
        ["juju-snapshot", "snapshot", "-f",
         join(work_dir, "runner", "snapshot.json")],
        stdout=open(join(work_dir, "runner", "restore.log"), "w"),
        stderr=subprocess.STDOUT)


def restore(work_dir):
    log.info("restoring environment")
    subprocess.check_call(
        ["juju-snapshot", "restore", "-f",
         join(work_dir, "runner", "snapshot.json")],
        stdout=open(join(work_dir, "runner", "restore.log"), "w"),
        stderr=subprocess.STDOUT)


def test(work_dir, job):
    log.info("waiting for test completion")
    try:
        subprocess.check_call(
            ["juju-watch", job['target']],
            stdout=open(join(work_dir, "runner", "watch.log"), "w"),
            stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError:
        return False
    return True


def record(test_record_path):
    log.info("assembling test report")
    subprocess.check_call(
        ["juju-record", "-f", test_record_path]
        )
    return test_record_path


def run(work_dir, job, test_record):
    snapshot(work_dir)
    try:
        load(work_dir, job)
        success = test(work_dir, job)
        record_path = record(test_record)
        return success, record_path
    except:
        log.exception("unknown error")
        return False, record(test_record)
    finally:
        restore(work_dir)


#######################
def worker(options):
    # Register
    while 1:
        try:
            token = register(
                options.job_queue_url, options.consumer_name)
        except ValueError:
            log.error("error retrieving token")
            sleep(options.poll_interval)
        else:
            break

    # Do work
    while True:
        setup_work_dir()
        job = poll(options.job_queue_url, token)
        if not job:
            sleep(options.poll_interval)
            continue
        t = time()
        success, record_path = run(job)
        result = {
            'success': success, 'test_time': time() - t, 'record': record_path
            }
        post_result(options.job_queue_url, token, job, result)


def setup_work_dir(work_dir):
    if os.path.exists(work_dir):
        shutil.rmtree(work_dir)
    os.makedirs(work_dir)
    os.mkdir(join(work_dir, "runner"))
    os.mkdir(join(work_dir, "plans"))
    os.mkdir(join(work_dir, "repo"))


def setup_parser():
    parser = argparse.ArgumentParser("Charm test runner")
    parser.add_argument("charm", nargs="*",
                        help="Charm to test")
    parser.add_argument("-s", "--series", required=True,
                        help="Charm series to use for tests")
    parser.add_argument("-w", "--work-dir", required=True,
                        help="Test runner working directory")
    parser.add_argument("-r", "--repository", required=True,
                        help="Charm repository for test planning")
    parser.add_argument("-t", "--test-record",
                        help="Path to store the test record zip")

    group = parser.add_argument_group('Queue Worker')
    group.add_argument("-j", "--job-queue-url",
                        help="HTTP charm test queue")
    group.add_argument("-c", "--consumer-name",
                        help="Worker name")
    group.add_argument("-p", "--poll-interval", default=40,
                        help="Work queue poll interval")

    return parser


def main():
    parser = setup_parser()
    options = parser.parse_args()
    setup_work_dir(options.work_dir)

    logging.basicConfig(
        level=logging.DEBUG,
        stream=open(join(options.work_dir, "runner", "runner.log"), "w"),
        format="%(asctime)s %(name)s:%(levelname)s %(message)s")
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(name)s:%(levelname)s %(message)s"))
    log.addHandler(handler)

    if options.job_queue_url:
        return worker(options)

    elif not options.charm:
        log.error("Charm name required")
        sys.exit(1)

    if not options.test_record:
        options.test_record = join(options.work_dir, "testrecord.zip")

    plan_iter = plan(options.repository,
                     options.work_dir,
                     options.charm[0],
                     options.series)
    success, result = run(options.work_dir, plan_iter.next(), options.test_record)
    sys.exit(bool(success))

if __name__ == '__main__':
    main()
