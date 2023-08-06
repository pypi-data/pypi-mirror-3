import argparse
import json
import logging
import os

from bzrlib.branch import Branch
from bzrlib.transport import get_transport

from graph import get_test_plan
from juju.charm.url import CharmCollection
from juju.charm.repository import LocalCharmRepository


log = logging.getLogger("jujitsu.planner")


class Repository(LocalCharmRepository):

    def iter(self, collection):
        return self._collection(collection)


def _get_bzr_info(charm):
    t = get_transport(charm.path)
    b = Branch.open_from_transport(t)
    p = b.get_parent()
    c = b.last_revision_info()[-1]
    return {"branch_spec": p, "commit": c}


def get_index(repository, series):
    repo = Repository(repository)
    series = CharmCollection("local", None, series)
    charms = []

    for charm in repo.iter(series):
        i_provides = []
        i_requires = []
        data = charm.metadata.get_serialization_data()
        for rel in data.get('provides', {}).values():
            i = rel.get('interface')
            if not i:
                continue
            i_provides.append(i)

        for rel in data.get('provides', {}).values():
            i = rel.get('interface')
            if not i:
                continue
            i_requires.append(i)

        data.update(_get_bzr_info(charm))
        data['i_provides'] = i_provides
        data['i_requires'] = i_requires
        data['owner'] = "charmers"
        data['series'] = series.series
        charms.append(data)
    return charms


def planner(options):
    log.info("Building index")
    index = get_index(options.repo, options.series)
    charm = options.charm[0]
    try:
        log.info("Generating plans")
        plans = list(get_test_plan(charm, series=options.series, index=index))
        log.info("Plans found %d", len(plans))
    except KeyError, e:
        e.args[0] == "c.%s" % charm
        log.error("Charm not found in repository %s" % charm)
        raise

    if options.plan_directory:
        plan_dir = os.path.abspath(options.plan_directory)
        for idx in range(len(plans)):
            p = plans[idx]
            pp = os.path.join(plan_dir, "%s-%d.plan" % (p['target'], idx))
            with open(pp, 'w') as fh:
                json.dump(p, fh, indent=2)
            log.debug("Wrote plan to %s" % pp)
    else:
        print json.dumps(plans[0], indent=2)


def setup_parser():
    parser = argparse.ArgumentParser("Test planner")
    parser.add_argument("charm", nargs="+")
    parser.add_argument(
        "-r", "--repo", required=True,
        help="Location of package repository")
    parser.add_argument(
        "-s", "--series", required=True,
        help="Release series to use")
    parser.add_argument(
        "-d", "--plan-directory", required=True,
        help="Save plans to directory")
    return parser


def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(name)s:%(levelname)s %(message)s")
    parser = setup_parser()
    options = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG)
    planner(options)

if __name__ == '__main__':
    main()
