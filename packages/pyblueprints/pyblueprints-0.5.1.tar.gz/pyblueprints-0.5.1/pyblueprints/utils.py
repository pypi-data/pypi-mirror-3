#!/usr/bin/env python
#-*- coding:utf-8 -*-

#####################################################################
# A set of utilities for Blueprints based graphs.                   #
#                                                                   #
# File: pyblueprints/utils.py                                       #
#####################################################################

def exportIndicesToNetworkx(graph, indices, debug=False):
    """Puts the information of the elements in the indices into a
    networkx structure.
    @params graph: blueprints graph object
    @params indices: A list of tuples with the information to be 
                    stored into networkx.
                    [(name, class, key, [values])
                    Being the name of the index, the key to be 
                    searched and the values that should match for
                    the given key.

    @returns The NetworkX structure created"""
    import networkx as nx
    nxGraph = nx.MultiDiGraph()
    for indexName, indexClass, key, values in indices:
        if indexClass == "vertex":
            idx = graph.getIndex(indexName, indexClass)
            for value in values:
                for vertex in idx.get(key, value):
                    properties = {}
                    for prop in vertex.getPropertyKeys():
                        properties[prop] = vertex.getProperty(prop)
                    nxGraph.add_node(vertex.getId(), properties)
                    if debug:
                        print "Added node %d: %s" %(vertex.getId(),
                                                    properties)
        elif indexClass == "edge":
            idx = graph.getIndex(indexName, indexClass)
            for value in values:
                for edge in idx.get(key, value):
                    #In vertex
                    vertex1 = edge.getInVertex()
                    properties = {}
                    for prop in vertex1.getPropertyKeys():
                        properties[prop] = vertex1.getProperty(prop)
                    nxGraph.add_node(vertex1.getId(), properties)
                    #Out vertex
                    vertex2 = edge.getOutVertex()
                    properties = {}
                    for prop in vertex2.getPropertyKeys():
                        properties[prop] = vertex2.getProperty(prop)
                    #Edge
                    nxGraph.add_node(vertex2.getId(), properties)
                    properties = {}
                    for prop in edge.getPropertyKeys():
                        properties[prop] = edge.getProperty(prop)
                    nxGraph.add_edge(vertex1.getId(),
                                        vertex2.getId(),
                                        key=edge.getLabel(),
                                        attr_dict=properties)
        else:
            raise TypeError("Unknown class %s" % indexClass)
    return nxGraph


