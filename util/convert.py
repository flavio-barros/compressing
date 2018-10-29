#!/usr/local/bin/python
# coding: utf-8

import networkx as nx
import re


def convert_input(file_path):
    """
    Converts input graph
    """
    graph = nx.nx_agraph.read_dot(file_path)
    converted_graph = nx.DiGraph()

    for node in graph.nodes:
        raw_formula(node)

    return converted_graph


def raw_formula(formula):

    if re.match(r'^.*[0-9]+$', formula):
        st = formula.split("  ")
        print formula
        print st
        print "\n"
    else:
        print formula
        print "\n"
