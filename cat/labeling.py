import networkx as nx
import numpy as np

def update_skeleton_with_nodetype( skeleton ):
    """ Add a nodetype property to each skeleton node of the graph
    as R (root), C (continuation), B (branch), E (end). """
    skeleton.graph.node[skeleton.root_node_id]['nodetype'] = 'R'
    for k,v in skeleton.graph.degree_iter():
        if v == 1 and not k == skeleton.root_node_id:
            skeleton.graph.node[ k ]['nodetype'] = 'E'
        elif v == 2:
        	skeleton.graph.node[ k ]['nodetype'] = 'C'
        elif v > 2:
            skeleton.graph.node[ k ]['nodetype'] = 'B'

def update_skeleton_with_connector_data( skeleton ):
    """ Add properties is_presynaptic and is_postsynaptic
    to skeleton nodes which evaluate to true if nodes are
    pre or postsynaptic. Additionaly, a upstream_skeleton and
    target_skeletons list refers to the skeleton ids associated
    with the connector. """
    for n, d in skeleton.graph.nodes_iter(data=True):
        d['is_presynaptic'] = 0
        d['is_postsynaptic'] = 0

    for connector_id, data in skeleton.connectors.items():
        if len( data['postsynaptic_to'] ) == 1:
            # postsynaptic contact to skeleton
            skeleton.graph.node[ data['postsynaptic_to'][0] ]['is_postsynaptic'] = 1
            skeleton.graph.node[ data['postsynaptic_to'][0] ]['upstream_skeleton'] = skeleton.connectordata[connector_id]['presynaptic_to']
        elif len( data['presynaptic_to'] ) == 1:
            # presynaptic contact to skeleton
            skeleton.graph.node[ data['presynaptic_to'][0] ]['is_presynaptic'] = 1
            skeleton.graph.node[ data['presynaptic_to'][0] ]['target_skeletons'] = skeleton.connectordata[connector_id]['postsynaptic_to']

def update_skeleton_edge_with_distance( skeleton ):
    """ Compute the Euclidian distance between two skeleton node locations
    and store the value as distance property on the skeleton edges. """
    for u,v,d in skeleton.graph.edges_iter(data=True):
        d['distance'] = np.linalg.norm( \
                    skeleton.graph.node[u]['location'] - \
                    skeleton.graph.node[v]['location'] )
