import json
import logging
import subprocess


log = logging.getLogger("jujitsu.env")


def deploy(repo_dir, charm, service=None):
    """Deploy a charm as a service.
    """
    args = ["juju", "deploy",
            "--repository", repo_dir,
            "local:%s" % charm]
    if service:
        args.append("%s" % service)
    output = subprocess.check_output(args, stderr=subprocess.STDOUT)
    log.info("Deployed %s" % (service or charm))
    return output


def destroy(service_name):
    output = subprocess.check_output(
        ["juju", "destroy-service", service_name],
        stderr=subprocess.STDOUT)
    log.debug("Destroyed %s" % (service_name))
    return output


def status(with_stderr=False):
    """Get a status dictionary.
    """
    args = ["juju", "status", "--format=json"]
    if with_stderr:
        output = subprocess.check_output(
            args, stderr=subprocess.STDOUT)
        return output
    else:
        output = subprocess.check_output(args, stderr=open("/dev/null"))
        return json.loads(output)


def add_relation(relation):
    """Add a relation.
    """
    args = ["juju", "add-relation"]
    args.extend(relation[:2])
    output = subprocess.check_output(args, stderr=subprocess.STDOUT)
    log.info("Added relation %s -> %s (%s)" % (
        relation[0], relation[1], relation[2]))
    return output


def is_bootstrapped():
    try:
        status(with_stderr=True)
    except:
        return False
    return True
