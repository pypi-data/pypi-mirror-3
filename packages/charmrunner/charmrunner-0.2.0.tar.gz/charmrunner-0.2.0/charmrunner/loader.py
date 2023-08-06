"""
Load an environment with charms and services

From test job
 -> Parse test plan
 -> Download/Update relevant charm versions (for now all to latest)
 -> Load environment
 ->

"""

import argparse
import logging
import json
import os
import shutil
import subprocess
import sys

from env import deploy, add_relation, is_bootstrapped


log = logging.getLogger("jujitsu.loader")
############################


def setup_repository(services, repo_dir, series):
    """Setup a repository.
    """
    if not os.path.exists(repo_dir):
        os.makedirs(repo_dir)

    if not os.path.isdir(repo_dir):
        raise ValueError("Invalid repository directory %s" % repo_dir)

    series_dir = os.path.join(repo_dir, series)

    if not os.path.exists(series_dir):
        os.makedirs(series_dir)

    for service in services:
        _bzr_branch(service, series_dir)


def _bzr_branch(info, series_dir):
    branch_dir = os.path.join(series_dir, info['charm'])
    log.debug("Branching charm lp:%s to %s", info["branch_spec"], branch_dir)

    if not info['branch_spec'].startswith("bzr+ssh"):
        info['branch_spec'] = "lp:%s" % info["branch_spec"]

    if not os.path.exists(branch_dir):
        subprocess.check_output(
            ["/usr/bin/bzr", "co", "-q", "--lightweight",
             info['branch_spec'],
             branch_dir],
            stderr=subprocess.STDOUT)

    output = subprocess.check_output(
        ["/usr/bin/bzr", "revision-info"], cwd=branch_dir,
        stderr=subprocess.STDOUT)
    revno, revid = output.strip().split()

    if revid == info["revid"]:
        log.info(
            "Retrieved charm %(charm)s from %(branch_spec)s" % info)

        return
    log.debug("Updating branch lp:%s", info["branch_spec"])
    try:
        output = subprocess.check_output(
            ["/usr/bin/bzr", "up", "-r", "revid:%s" % info["revid"]],
            stderr=subprocess.STDOUT)
    except:
        log.warning("Unable to fetch revision %s of %s ",
                    info['revid'], info['branch_spec'])

    log.info(
        "Retrieved charm %(charm)s from %(branch_spec)s@%(revid)s" % info)


def load_test_plan(test_plan, repo_dir):
    if not is_bootstrapped():
        print "Environment not bootstrapped"
        return sys.exit(1)

    setup_repository(
        test_plan['services'], repo_dir, test_plan['series'])

    for service in test_plan["services"]:
        deploy(repo_dir, service['charm'], service['charm'])

    for relation in test_plan["relations"]:
        add_relation(relation)


def setup_parser():
    parser = argparse.ArgumentParser(
        description="Bulk load services and relations into an environment")
    parser.add_argument("test_plan", default=False,
                        help="Test plan to load")
    parser.add_argument(
        "--reset-repo", default=False, action="store_true",
        help="Reset the repository between runs.")
    parser.add_argument(
        "-r", "--repo", required=True,
        help="Specify repository directory to use for charm downloads")

    return parser


def main():
    parser = setup_parser()
    options = parser.parse_args()
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(name)s:%(levelname)s %(message)s")

    with open(os.path.abspath(options.test_plan)) as fh:
        test_plan = json.loads(fh.read())

    try:
        load_test_plan(test_plan, options.repo)
    finally:
        if options.reset_repo and os.path.exists(options.repo):
            log.info("resetting repository")
            shutil.rmtree(os.path.abspath(options.repo))


if __name__ == '__main__':
    main()
