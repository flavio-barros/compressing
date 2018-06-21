#!/usr/local/bin/python
# coding: utf-8

from graph import Graph
import networkx as nx


class GraphAdapter(Graph):
    """
    This class uses the graph structure of the networkx library.
    See more: https://networkx.github.io
    """
    def __init__(self, file_path):
        self.graph = self.load_dot(file_path)

    def load_dot(self, file_path):
        agraph = nx.nx_agraph.read_dot(file_path)
        return nx.DiGraph(agraph)

    def to_agraph(self):
        return nx.nx_agraph.to_agraph(self.graph)

    def get_nodes(self):
        return list(self.graph.nodes)

    def set_node_attribute(self, node, attribute, value):
        self.graph.nodes[node][attribute] = value

    def get_node_attribute(self, node, attribute):
        if self.graph.nodes[node].has_key(attribute):
            return self.graph.nodes[node][attribute]
        return None

    def get_all_node_attributes(self, node):
        return self.graph.nodes[node]

    def get_in_neighbors(self, node):
        return list(self.graph.predecessors(node))

    def get_out_neighbors(self, node):
        return list(self.graph.successors(node))

    def get_in_edges(self, node):
        return self.graph.in_edges(node, data=False)

    def get_out_edges(self, node):
        return self.graph.out_edges(node, data=False)

    def get_in_degree(self, node):
        return self.graph.in_degree(node)

    def get_out_degree(self, node):
        return self.graph.out_degree(node)

    def remove_node(self, node):
        self.graph.remove_node(node)

    def get_edges(self):
        return list(self.graph.edges)

    def add_edge(self, source, target, **kwargs):
        self.graph.add_edge(source, target)
        if kwargs:
            for attribute, value in kwargs.items():
                self.graph.edges[source, target][attribute] = value

    def set_edge_attribute(self, source, target, attribute, value):
        self.graph.edges[source, target][attribute] = value

    def get_edge_attribute(self, source, target, attribute):
        if attribute in self.graph.edges[source, target]:
            return self.graph.edges[source, target][attribute]
        return None

    def get_all_edge_attributes(self, source, target):
        return self.graph.edges[source, target]

    def remove_edge(self, source, target):
        self.graph.remove_edge(source, target)

    def remove_edges(self, edges):
        self.graph.remove_edges_from(edges)
