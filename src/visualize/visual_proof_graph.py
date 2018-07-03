#!/usr/local/bin/python
# coding: utf-8

from src.util import constants
from src.visualize import visual_graph_adapter as vga


class VisualProofGraph:
    INPUT = constants.INPUT
    FINAL = constants.FINAL

    def __init__(self, graph):
        self.graph = graph
        self.vgraph = None

    def draw_input(self):
        self.vgraph = vga.VisualGraphAdapter(self.graph)
        self.__draw(VisualProofGraph.INPUT)

    def draw_final(self):
        self.vgraph = vga.VisualGraphAdapter(self.graph)
        self.__draw(VisualProofGraph.FINAL)

    def __draw(self, name):
        self.vgraph.set_name(name)
        self.__set_nodes_layout()
        self.__set_edges_layout()
        self.vgraph.draw_pdf()

    def __set_nodes_layout(self):
        for node in self.vgraph.get_nodes():
            formula = self.vgraph.get_node_attribute(node, constants.FORMULA)
            self.vgraph.set_node_attribute(node, vga.VisualGraphAdapter.LABEL,
                                           formula)
            is_hypothesis = self.vgraph.get_node_attribute(
                node, constants.HYPOTHESIS)
            if is_hypothesis:
                self.vgraph.set_node_attribute(node,
                                               vga.VisualGraphAdapter.XLABEL,
                                               "h")
                self.vgraph.set_node_attribute(node,
                                               vga.VisualGraphAdapter.COLOR,
                                               vga.VisualGraphAdapter.RED)
            del node.attr[constants.FORMULA], node.attr[constants.HYPOTHESIS]

    def __set_edges_layout(self):
        for (u, v) in self.vgraph.get_edges():
            edge = self.vgraph.get_edge(u, v)
            if edge.attr[constants.ANCESTOR] == constants.TRUE:
                self.vgraph.set_edge_attribute(u, v,
                                               vga.VisualGraphAdapter.COLOR,
                                               vga.VisualGraphAdapter.BLUE)
                self.vgraph.set_edge_attribute(u, v,
                                               vga.VisualGraphAdapter.FONTCOLOR,
                                               vga.VisualGraphAdapter.RED)
                self.vgraph.set_edge_attribute(u, v,
                                               vga.VisualGraphAdapter.XLABEL,
                                               str(edge.attr[constants.PATH]))
                del edge.attr[constants.PATH]
            elif edge.attr[constants.COLLAPSED] == constants.TRUE:
                self.vgraph.set_edge_attribute(u, v,
                                               vga.VisualGraphAdapter.XLABEL,
                                               constants.LAMBDA)
            else:
                self.vgraph.set_edge_attribute(u, v,
                                               vga.VisualGraphAdapter.XLABEL,
                                               str(edge.attr[constants.COLOR]))
                del edge.attr[constants.COLOR]
