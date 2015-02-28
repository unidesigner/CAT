import networkx as nx
import numpy as np

class Skeleton(object):

    def __init__(self, skeleton_id, graph ):
        self.skeleton_id = skeleton_id
        self.graph = graph

def get_skeleton(connection, skeleton_id):
    """ Fetch a skeleton from the database and return it as a Skeleton object containing
    a NetworkX graph for the morphology as nodes, edges between the skeleton nodes,
    and a mapping between node id and tag, and a mapping of all associated connectors. """

    d = connection.fetch('{0}/1/1/compact-skeleton'.format(skeleton_id))

    # create a graph representation of the skeleton
    g = nx.DiGraph()
    for treenode in d[0]:
        if treenode[1]:
            # Will create the nodes when not existing yet
            g.add_edge(treenode[1], treenode[0], {'confidence': treenode[7]})
        else:
            # The root node
            g.add_node(treenode[0])
        properties = g.node[treenode[0]]
        properties['user_id'] = treenode[2]
        properties['radius'] = treenode[6]
        properties['location'] = np.array([treenode[3], treenode[4], treenode[5]], dtype=np.float32)

    # tags are text vs list of treenode IDs, add them to the skeleton graph nodes as property
    for tag, treenodes in d[2].iteritems():
        for treenode_id in treenodes:
            tags = g[treenode_id].get('tags')
            if tags:
                tags.append(tag)
            else:
                g[treenode_id]['tags'] = [tag]

    # convert connectors into a lookup table
    connectors = {}
    relations = {0: 'presynaptic_to',
                 1: 'postsynaptic_to'}
    for connector in d[1]:
        treenode_id = connector[0]
        connector_id = connector[1]
        relation = relations[connector[2]]
        location = np.array( [connector[3], connector[4], connector[5]], dtype = np.float32 )
        if connector_id in connectors:
            connectors[connector_id][relation].append( treenode_id )
        else:
            connectors[connector_id] = {'location': location}
            connectors[connector_id]['presynaptic_to'] = []
            connectors[connector_id]['postsynaptic_to'] = []
            connectors[connector_id][relation].append( treenode_id )

    # for each connector of the skeleton, retrieve all associated relations
    # including their skeleton node id and skeleton id
    postdata = ''
    for i, connectorid in enumerate( map(str, connectors.keys() ) ):
        postdata += '&connector_ids%5B' + str(i) + '%5D=' + str( connectorid )
    results = connection.fetch('connector/skeletons', postdata)

    connectordata = {}
    if len( results ) != 0:
        for conn in results:
            connectordata[conn[0]] = conn[1]

    # retrieve the name of the neuron and its id
    neuron = connection.fetch('skeleton/{0}/neuronname'.format(skeleton_id))
    
    skeleton = Skeleton(skeleton_id, g)
    skeleton.root_node_id = find_root( g )
    skeleton.neuronname = neuron['neuronname']
    skeleton.neuron_id = neuron['neuronid']
    skeleton.connectors = connectors
    skeleton.connectordata = connectordata

    return skeleton

def find_root(tree):
    """ Search and return the first node that has zero predecessors.
    Will be the root node in directed graphs.
    Avoids one database lookup. """
    for node in tree:
        if not next(tree.predecessors_iter(node), None):
            return node
