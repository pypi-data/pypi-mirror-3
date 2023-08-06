import itertools


import networkx as nx

# on change, build interface index
# find all charms in a relation with this charm
# for each of those find any dependencies.
# if its a peer add a unit.


def get_charm_graph(owner="charmers", series="oneiric", index=()):
    g = nx.digraph.DiGraph()
    seen = set()

    for c in index:
        # Only construct the universe from charms
        if not c['owner'] == owner:
            continue
        if not c['series'] == series:
            continue
        name = "c.%s" % c['name']
        if name in seen:
            continue
        else:
            seen.add(name)
            g.add_node(
                name,
                branch_spec=c['branch_spec'].replace('/charm/', '/charms/'),
                commit=c['commit'])

        edges = []
        nodes = []

        for role_name, info in c.get("provides", {}).items():
            i = info['interface']
            edges.append(((name, i), {"role_name": role_name}))
            if i in seen:
                continue
            nodes.append(i)
            seen.add(i)

        for role_name, info in c.get("requires", {}).items():
            i = info['interface']
            edges.append(((i, name), {"role_name": role_name}))
            if i in seen:
                continue
            nodes.append(i)
            seen.add(i)

        g.add_nodes_from(nodes)
        for args, kw in edges:
            g.add_edge(*args, **kw)

    return g

# Blacklisted modules have semantic problems that should be fixed in
# charm metadata. Anything blacklisted will not be used to solve
# graphs.
BLACK_LIST = ["c.swift-proxy"]


def get_test_plan(charm_name, owner="charmers", series="oneiric", index=()):
    charm_id = "c.%s" % charm_name
    g = get_charm_graph(owner=owner, series=series, index=index)

    for plan_chain in _build_dependencies(g, charm_id):
        plan_chain = sort_plan(flatten_plan(plan_chain))
        charms = set()

        for p in plan_chain:
            charms.add(
                (p[0][2:],
                 g.node[p[0]]['branch_spec'],  # branch spec
                 g.node[p[0]]['commit'],  # commit
                 ))

            if p[1]:
                charms.add(
                    (p[1][2:],  # name
                     g.node[p[1]]['branch_spec'],  # branch spec
                     g.node[p[1]]['commit'],  # commit
                    ))

        charms = [
            dict(zip(("charm", "branch_spec", "revid"), x)) for x in charms]
        plan = {
            "target": charm_name,
            "series": series,
            "services": charms,
            "relations": list(_expand_relations(
                g,
                [[p[0][2:], p[1][2:], p[2]] for p in plan_chain if p[1]]))
            }

        yield plan


def _expand_relations(graph, relations):
    """Annotate relation info (source, target, interface)

    with role information.
    """

    for r in relations:
        source_role = graph.get_edge_data(
            "c.%s" % r[0], r[2]).get('role_name')

        target_role = graph.get_edge_data(
            r[2], "c.%s" % r[1]).get('role_name')

        source_id, target_id = r[0], r[1]
        if source_role:
            source_id = "%s:%s" % (source_id, source_role)
        if target_role:
            target_id = "%s:%s" % (target_id, target_role)

        yield (source_id, target_id, r[2])


def _build_dependencies(
    graph, charm_id, requested=None, source=None):
    """Build a sequence of plans to satisify the given `charm_id`,

    A plan represents a sequence of (charm_source, charm_target,
    interface) tuples.

    More specifically a plan represents a subgraph of traversal from
    each of ``charm_id`` dependent interfaces to an implementor of that
    interface.

    We try to flatten plan sequences so each represents a fulfillment.
    """
    providers = {}

    for interface, _ in graph.in_edges(charm_id):
        # skip self cycles (where a charm is both a provider and requirer)
        if (charm_id, interface) in graph.out_edges(charm_id):
            continue

        providers[interface] = []

        for provider, providing in graph.in_edges(interface):
            if provider in BLACK_LIST:
                continue
            for chain in (
                _build_dependencies(
                    graph, provider,
                    requested=providing,
                    source=charm_id)):
                providers[interface].append(chain)
                break  # pick the first solution

    if not providers:
        yield ((charm_id, source, requested))
        raise StopIteration()

    constraints = providers.keys()
    depth = len(constraints)

    # Generate and verify plans
    for plan in itertools.combinations(
        itertools.chain(*providers.values()), depth):
        required = set(constraints)
        for i in plan:
            if isinstance(i[0], basestring):
                if i[2] in required:
                    required.remove(i[2])
            elif isinstance(i[0], tuple):
                if i[0][2] in required:
                    required.remove(i[0][2])
        if required:
            continue
        yield ((charm_id, source, requested),) + plan


def sort_plan(plan):
    """Sort a sequence of relation tuples.

    A charm can only provide a relation if all of its
    dependencies are satisified.
    """
    plan = list(plan)
    #sources = [x[0] for x in plan]
    targets = [x[1] for x in plan]
    #relations = [x[2] for x in plan]

    dsu = []
    for i in plan:
        # make sure sources are after their targets
        if targets.count(i[0]):
            t_idx = targets.index(i[0]) + 1
            dsu.append((t_idx, i))
        else:
            dsu.append((0, i))
    dsu.sort()
    return [d[1] for d in dsu]


def flatten_plan(plan):
    """Flatten and unique nested sequence of relation plans into a flat set.

    Note, ordering is lost.
    """
    steps = set()

    if isinstance(plan, tuple) and isinstance(plan[0], basestring):
        steps.add(plan)
        return steps
    for p in plan:
        if isinstance(p, tuple) and isinstance(p[0], basestring):
            steps.add(p)
        else:
            steps.update(flatten_plan(p))
    return steps
