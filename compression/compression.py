#!/usr/local/bin/python
# coding: utf-8

from util import constants

"""
This module provide the necessary functions to perform the compression
on object from ProofGraph class.

Exported functions
------------------
get_nodes_repeated_formulas: return a list of lists with all repeated
    occurrences of nodes with identical labels in same level of
    derivation tree.

identify_rule: identifies the rule and return the corresponding
    function that perform the rule.

exec_rule: performs two-node collapse.
"""


def get_nodes_repeated_formulas(proof_graph):
    """
    Return a list with all nodes selected for compression. Each member
    list is a list with nodes that have identical formulas in the same
    level of derivation tree.

    The ProofGraph object has a attribute 'nodes_level', a
    dictionary-like object that stores nodes per level in derivation
    tree.

    Parameters
    ----------
    proof_graph: ProofGraph object

    Returns
    -------
    repeated_formulas: List
        A List of list of nodes with repeated formulas in same level of
        derivation tree.
    """
    repeated_formulas = []
    nodes_level = proof_graph.nodes_level
    for level, nodes in nodes_level.items():
        nodes_formula = {}
        for node in nodes:
            formula = proof_graph.get_node_attribute(node,
                                                     constants.FORMULA)
            if formula in nodes_formula:
                nodes_formula[formula].append(node)
            else:
                nodes_formula[formula] = [node]
        for formula, nodes2 in nodes_formula.items():
            if len(nodes2) > 1:
                repeated_formulas.append(nodes2)
        level += 1
    return repeated_formulas


def identify_rule(graph, node_u, node_v):
    """
    Returns the appropriate function that performs the collapse of
    nodes node_u and node_v.

    Parameters
    ----------
    graph: ProofGraph object

    node_u, node_v: nodes
        Nodes in proof graph

    Returns
    -------
    function: function
        Function that performs the collapse of nodes
    """
    in_degree_u = graph.get_deductive_in_degree(node_u)
    in_degree_v = graph.get_deductive_in_degree(node_v)

    out_degree_u = graph.get_deductive_out_degree(node_u)
    out_degree_v = graph.get_deductive_out_degree(node_v)

    ancestor_target_u = graph.get_node_attribute(node_u, graph.ANCESTOR_TARGET)
    ancestor_target_v = graph.get_node_attribute(node_v, graph.ANCESTOR_TARGET)

    if not ancestor_target_u and not ancestor_target_v:
        if (in_degree_u > 0 and in_degree_v > 0) and (
                out_degree_u == 1 and out_degree_v == 1):
            return rule_1
        elif (in_degree_u == 0 or in_degree_v == 0) and (
                out_degree_u == 1 and out_degree_v == 1):
            if in_degree_u == 0 and in_degree_v == 0:
                return rule_4
            elif in_degree_u == 0:
                return rule_2
            elif in_degree_v == 0:
                return rule_3
        elif out_degree_u > 1 or out_degree_v > 1:
            if in_degree_u > 0 and in_degree_v > 0:
                return rule_5
            else:
                return rule_6
    elif ancestor_target_u and ancestor_target_v:
        if is_connected_same_node(graph, node_u, node_v):
            if in_degree_u > 0 and in_degree_v > 0:
                return rule_7
            elif in_degree_u > 0 and in_degree_v == 0:
                return rule_8
            elif in_degree_u == 0 and in_degree_v > 0:
                return rule_9
            else:
                return rule_10
        else:
            if in_degree_u > 0 and in_degree_v > 0:
                return rule_11
            elif in_degree_u > 0 and in_degree_v == 0:
                return rule_12
            elif in_degree_u == 0 and in_degree_v > 0:
                return rule_13
            else:
                return rule_14
    elif ancestor_target_u or ancestor_target_v:
        if is_connected_same_node(graph, node_u, node_v):
            if in_degree_u == 0 or in_degree_v == 0:
                return rule_16
            elif in_degree_u > 0 and in_degree_v > 0:
                return rule_15
        else:
            if in_degree_u == 0 or in_degree_v == 0:
                return rule_18
            elif in_degree_u > 0 and in_degree_v > 0:
                return rule_17


def exec_rule(rule_function, graph, node_u, node_v):
    """
    Performs the collapse of nodes and returns the collapsed node.

    Parameters
    ----------
    rule_function: function
        Function that performs the collapse

    graph: ProofGraph object.

    node_u, node_v: nodes
        Nodes in graph

    Returns
    -------
    collapsed_node: node
        Collapsed node.
    """
    global seq_collapse
    collapsed_node = rule_function(graph, node_u, node_v)
    seq_collapse += 1
    return collapsed_node


def rule_1(graph, node_u, node_v):
    prepare_collapse(graph, node_u, color=1)
    prepare_collapse(graph, node_v, color=2)
    collapse_nodes(graph, node_u, node_v)
    return node_u


def rule_2(graph, node_u, node_v):
    prepare_collapse(graph, node_v, color=1)
    collapse_nodes(graph, node_u, node_v)
    graph.set_node_attribute(node_u, graph.HYPOTHESIS, True)
    return node_u


def rule_3(graph, node_u, node_v):
    prepare_collapse(graph, node_u, color=1)
    collapse_nodes(graph, node_u, node_v)
    graph.set_node_attribute(node_u, graph.HYPOTHESIS, True)
    return node_u


def rule_4(graph, node_u, node_v):
    collapse_nodes(graph, node_u, node_v)
    graph.set_node_attribute(node_u, graph.HYPOTHESIS, True)
    return node_u


def rule_5(graph, node_u, node_v):
    if graph.get_deductive_out_degree(node_u) > 1:
        max_color_u = maximal_color(graph, node_u)
        prepare_collapse(graph, node_v, color=max_color_u + 1)
        collapse_nodes(graph, node_u, node_v)
        return node_u
    else:
        max_color_v = maximal_color(graph, node_v)
        prepare_collapse(graph, node_u, color=max_color_v + 1)
        collapse_nodes(graph, node_v, node_u)
        return node_v


def rule_6(graph, node_u, node_v):
    if graph.get_deductive_out_degree(node_u) > 1:
        collapse_nodes(graph, node_u, node_v)
        graph.set_node_attribute(node_u, graph.HYPOTHESIS, True)
        return node_u
    else:
        collapse_nodes(graph, node_v, node_u)
        graph.set_node_attribute(node_v, graph.HYPOTHESIS, True)
        return node_v


def rule_7(graph, node_u, node_v):
    prepare_collapse(graph, node_u)
    prepare_collapse(graph, node_v)
    collapse_nodes(graph, node_u, node_v, collapse_edge=True)
    return node_u


def rule_8(graph, node_u, node_v):
    prepare_collapse(graph, node_u)
    collapse_nodes(graph, node_u, node_v, collapse_edge=True,
                   ancestor_edges=True)
    graph.set_node_attribute(node_u, graph.HYPOTHESIS, True)
    return node_u


def rule_9(graph, node_u, node_v):
    prepare_collapse(graph, node_v)
    collapse_nodes(graph, node_u, node_v, collapse_edge=True)
    graph.set_node_attribute(node_u, graph.HYPOTHESIS, True)
    return node_u


def rule_10(graph, node_u, node_v):
    collapse_nodes(graph, node_u, node_v, ancestor_edges=True)
    graph.set_node_attribute(node_u, graph.HYPOTHESIS, True)
    return node_u


def rule_11(graph, node_u, node_v):
    prepare_collapse(graph, node_u, color=1)
    prepare_collapse(graph, node_v, color=2)
    collapse_nodes(graph, node_u, node_v)
    return node_u


def rule_12(graph, node_u, node_v):
    prepare_collapse(graph, node_u, color=1)
    collapse_nodes(graph, node_u, node_v, ancestor_edges=True)
    graph.set_node_attribute(node_u, graph.HYPOTHESIS, True)
    return node_u


def rule_13(graph, node_u, node_v):
    prepare_collapse(graph, node_v, color=1)
    collapse_nodes(graph, node_u, node_v)
    graph.set_node_attribute(node_u, graph.HYPOTHESIS, True)
    return node_u


def rule_14(graph, node_u, node_v):
    collapse_nodes(graph, node_u, node_v, ancestor_edges=True)
    graph.set_node_attribute(node_u, graph.HYPOTHESIS, True)
    return node_u


def rule_15(graph, node_u, node_v):
    if graph.get_node_attribute(node_u, graph.ANCESTOR_TARGET):
        prepare_collapse(graph, node_u)
        collapse_nodes(graph, node_v, node_u, collapse_edge=True)
        return node_v
    else:
        prepare_collapse(graph, node_v)
        collapse_nodes(graph, node_u, node_v, collapse_edge=True)
        return node_u


def rule_16(graph, node_u, node_v):
    if graph.get_node_attribute(node_u, graph.ANCESTOR_TARGET):
        collapse_nodes(graph, node_v, node_u, collapse_edge=True,
                       ancestor_edges=True)
        graph.set_node_attribute(node_v, graph.HYPOTHESIS, True)
        return node_v
    else:
        collapse_nodes(graph, node_u, node_v, collapse_edge=True,
                       ancestor_edges=True)
        graph.set_node_attribute(node_u, graph.HYPOTHESIS, True)
        return node_u


def rule_17(graph, node_u, node_v):
    if graph.get_node_attribute(node_u, graph.ANCESTOR_TARGET):
        max_color_v = maximal_color(graph, node_v)
        prepare_collapse(graph, node_u, color=max_color_v + 1)
        collapse_nodes(graph, node_v, node_u)
        return node_v
    else:
        max_color_u = maximal_color(graph, node_u)
        prepare_collapse(graph, node_v, color=max_color_u + 1)
        collapse_nodes(graph, node_u, node_v)
        return node_u


def rule_18(graph, node_u, node_v):
    if graph.get_node_attribute(node_u, graph.ANCESTOR_TARGET):
        collapse_nodes(graph, node_v, node_u, ancestor_edges=True)
        graph.set_node_attribute(node_v, graph.HYPOTHESIS, True)
        return node_v
    else:
        collapse_nodes(graph, node_u, node_v, ancestor_edges=True)
        graph.set_node_attribute(node_u, graph.HYPOTHESIS, True)
        return node_u


def prepare_collapse(graph, node, color=None):
    """
    Prepare the node for collapse.

    Adds ancestor edges or redirects them.

    Update the path of ancestor edge.

    Coloring the edge if node is not None.

    Parameters
    ----------
    graph: GraphAdapter object

    node: node
        Node in graph

    color: int
        If color is given, set color of out edge with it.
    """
    is_ancestor_target = graph.get_node_attribute(node, graph.ANCESTOR_TARGET)
    if is_ancestor_target:
        redirect_ancestor_edges(graph, node, color)
    else:
        add_ancestor_edges(graph, node, color)

    if color:
        out_neighbor, = graph.get_deductive_out_neighbors(node)
        graph.set_edge_attribute(node, out_neighbor, graph.COLOR, color)


def collapse_nodes(graph, node_u, node_v, collapse_edge=None,
                   ancestor_edges=None):
    """
    Collapses node_u and node_v.

    Redirects in and out edges of node_v to node_v.

    Remove node_v.

    Parameters
    ----------
    graph: GraphAdapter object

    node_u, node_v: nodes
        Nodes in the graph

    collapse_edge: boolean
        If True, collapse edges

    ancestor_edges: boolean
        If True, redirect ancestor edges
    """
    if collapse_edge:
        for (source_u, target_u) in graph.get_out_edges(node_u):
            for (source_v, target_v) in graph.get_out_edges(node_v):
                if target_u == target_v:
                    graph.collapse_edges(node_u, node_v, target_u)

    if ancestor_edges:
        graph.redirect_in_edges(node_v, node_u, ancestor_edges=True)
    else:
        graph.redirect_in_edges(node_v, node_u)
    graph.redirect_out_edges(node_v, node_u)
    graph.remove_node(node_v)


def redirect_ancestor_edges(graph, node, color):
    """
    Redirect in ancestor edges of node node to predecessor nodes.

    Parameters
    ----------
    graph: GraphAdapter object

    node: node
        Node in the graph

    color: int
        If color is given, add it in edge path.

    """
    ancestor_edges = graph.get_ancestor_in_edges(node)
    deductive_edges = graph.get_deductive_in_edges(node)

    for (ancestor_source, ancestor_target) in ancestor_edges:
        path = graph.get_edge_attribute(ancestor_source, ancestor_target,
                                        graph.PATH)
        for (deductive_source, deductive_target) in deductive_edges:
            if color:
                graph.add_ancestor_edge(ancestor_source, deductive_source,
                                        path=path, new_color=color)
            else:
                graph.add_ancestor_edge(ancestor_source, deductive_source,
                                        path=path)
            graph.set_node_attribute(deductive_source, graph.ANCESTOR_TARGET,
                                     True)
    graph.remove_edges(ancestor_edges)
    graph.set_node_attribute(node, graph.ANCESTOR_TARGET, False)


def add_ancestor_edges(graph, node, color):
    """
    Add ancestor edges between out_neighbor and in_neighbor(s) of the
    node.

    Parameters
    ----------
    graph: GraphAdapter object

    node: node
        Node in the graph

    color: int
        Color is added to edge path
    """
    out_neighbor, = graph.get_deductive_out_neighbors(node)
    for in_neighbor in graph.get_deductive_in_neighbors(node):
        graph.add_ancestor_edge(out_neighbor, in_neighbor, new_color=color)
        graph.set_node_attribute(in_neighbor, graph.ANCESTOR_TARGET, True)


def is_connected_same_node(graph, node_u, node_v):
    """
    Return True if exists a node that is out_neighbor of node_u and
    node_v. Return False if this node not exists.

    Parameters
    ----------
    graph: GraphAdapter object

    node_u, node_v: nodes
        Nodes in the graph
    """
    for out_neighbor_u in graph.get_deductive_out_neighbors(node_u):
        for out_neighbor_v in graph.get_deductive_out_neighbors(node_v):
            if out_neighbor_u == out_neighbor_v:
                return True
    return False


def maximal_color(graph, node):
    """
    Return the maximal color of out_edges of node.

    Parameters
    ----------
    graph: GraphAdapter object

    node: node
        Node in the graph
    """
    max_color = 0
    for (source, target) in graph.get_deductive_out_edges(node):
        is_collapsed = graph.get_edge_attribute(source, target,
                                                graph.COLLAPSED)
        if not is_collapsed:
            color = graph.get_edge_attribute(source, target, graph.COLOR)
            if color > max_color:
                max_color = color
    return max_color


seq_collapse = 0
