#!/usr/local/bin/python
# coding: utf-8

from src import constants
import visual_graph as vig


class VisualGraphAdapter(vig.VisualGraph):

    UPPER = constants.UPPER
    LOWER = constants.LOWER
    SAME = constants.SAME

    XLABEL = constants.XLABEL
    FONTCOLOR = constants.FONTCOLOR
    LABEL = constants.LABEL
    COLOR = constants.COLOR

    RED = constants.RED
    BLUE = constants.BLUE

    def __init__(self, graph):
        self.agraph = graph.to_agraph()
        self.name = None
        self.path = "pdf/{0}.pdf"

    def draw_pdf(self):
        file_path = self.path.format(self.name)
        self.agraph.draw(file_path, prog="dot")

    def get_nodes(self):
        return self.agraph.nodes()

    def get_edges(self):
        return self.agraph.edges()

    def get_edge(self, u, v):
        return self.agraph.get_edge(u, v)

    def get_node(self, node):
        return self.agraph.get_node(node)

    def set_name(self, name):
        self.name = name

    def set_edge_attribute(self, u, v, attribute, value):
        edge = self.agraph.get_edge(u, v)
        edge.attr[attribute] = value

    def get_edge_attribute(self, u, v, attribute):
        edge = self.agraph.get_edge(u, v)
        if attribute in edge.attr:
            attribute_value = edge.attr[attribute]
            if attribute_value == constants.TRUE:
                return True
            elif attribute_value == constants.FALSE:
                return False
            else:
                return attribute_value
        return None

    def set_node_attribute(self, node, attribute, value):
        node = self.agraph.get_node(node)
        node.attr[attribute] = value

    def get_node_attribute(self, node, attribute):
        node = self.agraph.get_node(node)
        if node.attr.has_key(attribute):
            attribute_value = node.attr[attribute]
            if attribute_value == constants.TRUE:
                return True
            elif attribute_value == constants.FALSE:
                return False
            else:
                return attribute_value

    def set_nodes_orientation(self, nodes, orientation):
        self.agraph.add_subgraph(nodes, rank=orientation)
