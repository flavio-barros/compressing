#!/usr/local/bin/python
# coding: utf-8

from util import constants
from visualize import visual_graph as vgr


class VisualGraphAdapter(vgr.VisualGraph):
    """
    This class uses the graph_structure structure of the pygraphviz library.

    This class is used to generate PDF files of graph_structure visualization.

    See more: http://pygraphviz.github.io/
    """

    # Nodes orientation
    UPPER = constants.UPPER
    LOWER = constants.LOWER
    SAME = constants.SAME

    # Edges and nodes attributes
    XLABEL = constants.XLABEL
    FONTCOLOR = constants.FONTCOLOR
    LABEL = constants.LABEL
    COLOR = constants.COLOR

    # Colors
    RED = constants.RED
    BLUE = constants.BLUE

    def __init__(self, graph):
        """
        Initializes a VisualGraphAdapter instance.

        Set 'graph_structure' to instance variable 'graph_structure' (AGraph type).

        Creates 'name' and 'path' variables.

        All generated files are in "pdf" directory.

        Parameters
        ----------
        graph: GraphAdapter object
        """
        self.agraph = graph.to_agraph()
        self.name = None
        self.path = "pdf/{0}.pdf"

    def set_name(self, name):
        """
        Set name to instance variable 'name'

        """
        self.name = name

    def draw_pdf(self):
        """
        Generates PDF file from instance variable 'graph_structure'.

        The PDF file is saved in 'path' (instance variable) and with
        'name' (instance variable).
        """
        file_path = self.path.format(self.name)
        self.agraph.draw(file_path, prog="dot")

    def get_nodes(self):
        """
        Return a list with all nodes in graph_structure.

        Returns
        -------
        nodes: List
            List with all nodes in graph_structure.
        """
        nodes = self.agraph.nodes()
        return nodes

    def get_edges(self):
        """
        Return a list with all edges (u, v) in graph_structure.

        Returns
        -------
        edges: List
            List with all edges in graph_structure.
        """
        return self.agraph.edges()

    def get_edge(self, source, target):
        """
        Return the edge object between source and target.

        Parameters
        ----------
        source, target: nodes
            Nodes in the graph_structure
        """
        return self.agraph.get_edge(source, target)

    def get_node(self, n):
        """
        Return the node object corresponding to 'n'

        Parameters
        ----------
        n: node
            Node in the graph_structure

        Returns
        -------
        node: node object
            Node in the graph_structure
        -------
        """
        node = self.agraph.get_node(n)
        return node

    def set_edge_attribute(self, source, target, attribute, value):
        """
        Assign value to edge attribute.

        Parameters
        ----------
        source, target: hashable type
            Nodes in the graph_structure

        attribute: hashable type
            edge attribute

        value: int, string or boolean
            Value of edge attribute
        """
        edge = self.agraph.get_edge(source, target)
        edge.attr[attribute] = value

    def get_edge_attribute(self, source, target, attribute):
        """
        Returns the edge attribute.

        If edge attribute is equal to "True" of "False", return
        boolean value, True or False.

        Parameters
        ----------
        source, target: hashable type
            Nodes in the graph_structure

        attribute: hashable type
            Node attribute
        """
        edge = self.agraph.get_edge(source, target)
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
        """
        Assign value to node attribute.

        Parameters
        ----------
        node: hashable type
            Node in the graph_structure

        attribute: hashable type
            Node attribute

        value: int, string or boolean
            Value of node attribute
        """
        node = self.agraph.get_node(node)
        node.attr[attribute] = value

    def get_node_attribute(self, node, attribute):
        """
        Returns the node attribute.

        If node attribute is equal to "True" of "False", return
        boolean value, True or False.

        Parameters
        ----------
        node: hashable type
            Node in the graph_structure

        attribute: hashable type
            Node attribute
        """
        node = self.agraph.get_node(node)
        if attribute in node.attr:
            attribute_value = node.attr[attribute]
            if attribute_value == constants.TRUE:
                return True
            elif attribute_value == constants.FALSE:
                return False
            else:
                return attribute_value

    def set_nodes_orientation(self, nodes, orientation):
        """
        Creates a subgraph with nodes and set orientation.

        Orientation can be UPPER, SAME or LOWER. (class variables)
        """
        self.agraph.add_subgraph(nodes, rank=orientation)