#!/usr/local/bin/python
# coding: utf-8

from graph.proof_graph import ProofGraph
from flow import FlowColor, FlowEdge
import re

# Color -1 represents lambda (collapsed edge)
LAMBDA = -1
IMPLICATION = "->"
COLORS = None


def verifying(graph):
    """
    Parameters
    ----------
    graph: ProofGraph object
    """

    mark_hypothesis(graph)
    set_lambda_color(graph)

    # Dictionary storing nodes per level
    nodes_level = graph.get_nodes_level()

    # Building decreasing list from max_level to 0
    max_level = max(nodes_level.keys())
    levels = range(max_level, -1, -1)

    # Building decreasing list from max_color to 0
    max_color = max(graph.formulas_index.values())
    global COLORS
    COLORS = range(max_color, -2, -1)

    flow1 = FlowEdge()
    flow2 = FlowColor(graph.formulas_index)

    for level in levels:
        print "Nivel", level
        for node in nodes_level[level]:
            formula = graph.get_node_attribute(node, ProofGraph.FORMULA)
            print "Formula", formula
            for color in COLORS:
                print "Color", color
                print "flow1", flow1.dictionary
                premisses = premiss(graph, flow1, node, color)
                print "premiss()", premisses
                is_hypothesis = graph.get_node_attribute(node,
                                                         ProofGraph.HYPOTHESIS)
                if is_hypothesis:
                    print "Hypothesis", is_hypothesis
                    if color == 0:
                        if not premisses:
                            flow2.set(0, formula, None)
                        else:
                            message = "vertex 'p' as regular (not related to " \
                                      "lambda-edges) hypothesis cannot have " \
                                      "incoming edges or premisses"
                            raise InvalidException(message)
                    else:
                        if not premisses:
                            is_ancestor_target = graph.get_node_attribute(
                                    node, ProofGraph.ANCESTOR_TARGET)
                            if is_ancestor_target:

                                ancestor_edges = graph.get_ancestor_in_edges(
                                        node)
                                for edge in ancestor_edges:
                                    path = graph.get_edge_attribute(
                                        edge[0], edge[1], ProofGraph.PATH)
                                    get_path_head(path)
                                    get_path_tail(path)
                            else:
                                flow2.set(color, None, None)
                        else:
                            dependencies, path = \
                                update_partial_flow(graph, premisses, node,
                                                    color, flow1)
                            flow2.set(color, dependencies, path)
                else:
                    print "Hypothesis", is_hypothesis
                    if color == 0:
                        if not premisses:
                            message = "hypothesis should not have premisses"
                            raise InvalidException(message)
                        else:
                            dependencies, path = \
                                update_partial_flow(graph, premisses, node,
                                                    color, flow1)
                            flow2.set(color, dependencies, path)
                    else:
                        if not premisses:
                            flow2.set(color, None, None)
                        else:
                            dependencies, path = \
                                update_partial_flow(graph, premisses, node,
                                                    color, flow1)
                            flow2.set(color, dependencies, path)
                print ""

            lambda_edges = get_lambda_edges(graph, node)
            out_edges = graph.get_deductive_out_edges(node)
            not_lambda_edges = list(set(out_edges) - set(lambda_edges))

            updated_colors = []
            for (s, t) in not_lambda_edges:
                e_color = graph.get_edge_attribute(s, t, graph.COLOR)
                updated_colors.append(e_color)
                if e_color == 0:
                    flow1.set(s, t, 0, flow2.get(0))
                elif e_color > 0:
                    if not flow1.get(s, t, e_color):
                        flow1.set(s, t, e_color, flow2.get(e_color))
                    else:
                        message = "S1 already defined, should not pass by " \
                                  "initial check of decorated rooted dag"
                        raise InvalidException(message)
                else:
                    message = "undefined color of edge"
                    raise InvalidException(message)

            colors = range(0, max_color + 1)
            colors = list(set(colors) - (set(updated_colors)))
            for (s, t) in lambda_edges:
                for c in colors:
                    flow1.set(s, t, c, flow2.get(c))

            flow2.reset()
    print "Verificação inicial concluída"
    # Check if derivation is valid


def get_lambda_edges(graph, node):
    out_edges = graph.get_deductive_out_edges(node)
    lambda_edges = []

    for (s, t) in out_edges:
        is_collapsed = graph.get_edge_attribute(s, t, graph.COLLAPSED)
        if is_collapsed:
            lambda_edges.append((s, t))

    return lambda_edges


def premiss(graph, flow, node, color):
    edges_color = flow.get_edges_by_color(color)
    print "edges_color", edges_color
    edges = edges_target(edges_color, node)
    if color > 0:
        print "suitable", suitable(edges)
        if suitable(edges):
            if not edges:
                return {}
            else:
                return {color: edges}
        else:
            message = "incoming edges are not suitable premises"
            raise InvalidException(message)
    elif color == 0:
        is_hypothesis = graph.get_node_attribute(node, ProofGraph.HYPOTHESIS)
        if is_hypothesis:
            if not edges:
                return {}
            else:
                message = "a hypothesis has no premisses of color 0"
                raise InvalidException(message)
        else:
            if not edges:
                message = "only hypothesis have empty set of premisses"
                raise InvalidException(message)
            else:
                if not edges:
                    return {}
                else:
                    return {color: edges}
    elif color == LAMBDA:
        f = {}
        global COLORS
        colors = set(COLORS)-{-1}
        has_edges = False
        for c in colors:
            edges_c = flow.get_edges_by_color(c)
            edges_t = edges_target(edges_c, node)
            f[c] = edges_t
            if edges_t:
                has_edges = True
        if has_edges:
            return f
        else:
            return {}
    else:
        message = "invalid color"
        raise InvalidException(message)


# Verifying if premises are suitable to conclusion
def suitable(edges):
    if not edges:
        return True
    else:
        if len(edges) == 1 or len(edges) == 2:
            return True
        else:
            print False


def update_partial_flow(graph, premisses, node, color, flow):
    edges_out = get_out_edge_color(graph, node, color)
    premisses_cardinality = get_premises_cardinality(premisses)

    if edges_out == 1 and color != LAMBDA:
        edge, = edges_out
        if premisses_cardinality == 2:
            if is_imp_elimination(graph, premisses, edge, flow, color):
                dependencies_minor, path_minor = get_minor_premiss(graph,
                                                                   premisses)
                dependencies_major, path_major = get_major_premiss(graph,
                                                                   premisses)
                dependencies = dependencies_minor ^ dependencies_major
                return dependencies, path_minor[1:]
            else:
                message = "Wrong application of ->-E rule. Cannot update flow"
                raise InvalidException(message)
        elif premisses_cardinality == 1:
            if is_imp_introduction_lambda(graph, premisses, edge, flow, color):
                single_premiss = get_single_premiss(premisses)
                dependencies_premiss, path_premiss = flow.get(single_premiss[0],
                                                              single_premiss[1],
                                                              color)

                formula = graph.get_node_attribute(node, ProofGraph.FORMULA)
                formula_antecedent = get_antecedent(formula)
                index_antecedent = graph.formulas_index[formula_antecedent]

                dependencies_premiss[index_antecedent] = 0

                return dependencies_premiss, path_premiss[1:]
            else:
                message = "Wrong application of ->-I rule. Cannot update flow"
                raise InvalidException(message)
        else:
            message = "Wrong application of rule. Cannot update flow"
            raise InvalidException(message)
    elif color == LAMBDA:
        edge, = edges_out
        if premisses_cardinality == 2:
            if is_imp_elimination_lambda(graph, premisses, edge, flow, color):
                dependencies_minor, path_minor = get_minor_premiss(graph,
                                                                   premisses)
                dependencies_major, path_major = get_major_premiss(graph,
                                                                   premisses)
                dependencies = dependencies_minor ^ dependencies_major
                return dependencies, path_minor[1:]
            else:
                message = "Wrong application of ->-E rule. Cannot update flow"
                raise InvalidException(message)
        elif premisses_cardinality == 1:
            if is_imp_introduction_lambda(graph, premisses, edge, flow, color):
                single_premiss = get_single_premiss(premisses)
                dependencies_premiss, path_premiss = flow.get(single_premiss[0],
                                                              single_premiss[1],
                                                              color)

                formula = graph.get_node_attribute(node, ProofGraph.FORMULA)
                formula_antecedent = get_antecedent(formula)
                index_antecedent = graph.formulas_index[formula_antecedent]

                dependencies_premiss[index_antecedent] = 0

                return dependencies_premiss, path_premiss[1:]
            else:
                message = "Wrong application of ->-I rule. Cannot update flow"
                raise InvalidException(message)
        else:
            message = "Wrong application of rule. Cannot update flow"
            raise InvalidException(message)
    else:
        message = "Wrong application of rule. Cannot update flow"
        raise InvalidException(message)


def get_path_head(path):
    if not path:
        message = "Head path don't exists"
        raise InvalidException(message)
    else:
        return path[0]


def get_path_tail(path):
    tail = path[1:]

    if not tail:
        message = "Tail path don't exists"
        raise InvalidException(message)
    else:
        return tail


def get_premises_cardinality(premisses):
    card = 0
    for color, edges in premisses.items():
        card += len(edges)
    return card


def is_implication(formula):
    non_atomic_antecedent_re = r"^(\([0-9a-zA-Z]+.imp.[0-9a-zA-Z]+\)).imp.(.*)$"
    atomic_antecedent_re = r"^\(([0-9a-zA-Z]*).imp.(.*)\)$"
    atomic_re = r"^([0-9a-zA-Z]*)$"
    if re.match(non_atomic_antecedent_re, formula):
        match = re.search(non_atomic_antecedent_re, formula)
        return True, (match.group(1), match.group(2))
    elif re.match(atomic_antecedent_re, formula):
        match = re.search(atomic_antecedent_re, formula)
        return True, (match.group(1), match.group(2))
    elif re.match(atomic_re, formula):
        return False, None
    else:
        print "NOT MATCH"
    print ""


def is_imp_elimination(graph, premisses, edge, flow, color):
    u, v = edge

    minor_premiss = get_minor_premiss(graph, premisses)
    major_premiss = get_major_premiss(graph, premisses)

    dependencies1, path1 = flow.get(minor_premiss[0], minor_premiss[1], color)
    dependencies2, path2 = flow.get(major_premiss[0], major_premiss[1], color)

    # Check formulas
    label_source = get_label_source(graph, edge)
    formula_minor = get_label_source(minor_premiss)
    formula_major = get_label_source(major_premiss)

    formula1 = formula_minor+IMPLICATION+label_source
    formula2 = formula_major

    equal_formulas = formula1 == formula2

    # check dependencies
    dependencies_premisses = dependencies1 ^ dependencies2
    dependencies = graph.get_edge_attribute(u, v, ProofGraph.DEPENDENCIES)

    equal_dependencies = dependencies_premisses == dependencies

    # check paths
    equal_paths = path1 == path2

    # return
    return equal_formulas and equal_dependencies and equal_paths


def is_imp_introduction(graph, premisses, edge, flow, color):
    u, v = edge

    single_premiss = get_single_premiss(premisses)
    formula = get_label_source(single_premiss)

    antecedent = get_antecedent(formula)
    consequent = get_consequent(formula)

    # check formulas
    equal_formulas = formula == consequent

    # check dependencies
    dependencies_p, path_p = flow.get(single_premiss[0], single_premiss[1],
                                      color)
    index_ant = graph.formulas_index[antecedent]
    dependencies_p[index_ant] = 0

    dependencies_edge = graph.get_edge_attribute(u, v, graph.DEPENDENCIES)

    equal_dependencies = dependencies_p == dependencies_edge

    # return
    return equal_formulas and equal_dependencies


def is_imp_elimination_lambda(graph, premisses, edge, flow, color):
    minor_premiss = get_minor_premiss(graph, premisses)
    major_premiss = get_major_premiss(graph, premisses)

    dependencies1, path1 = flow.get(minor_premiss[0], minor_premiss[1], color)
    dependencies2, path2 = flow.get(major_premiss[0], major_premiss[1], color)

    # Check formulas
    label_source = get_label_source(graph, edge)
    formula_minor = get_label_source(minor_premiss)
    formula_major = get_label_source(major_premiss)

    formula1 = formula_minor + IMPLICATION + label_source
    formula2 = formula_major

    equal_formulas = formula1 == formula2

    # check paths
    equal_paths = path1 == path2

    return equal_formulas and equal_paths


def is_imp_introduction_lambda(graph, premisses, edge, flow, color):
    single_premiss = get_single_premiss(premisses)
    formula = get_label_source(single_premiss)

    consequent = get_consequent(formula)

    # check formulas
    equal_formulas = formula == consequent

    # return
    return equal_formulas


def get_minor_and_major_premiss(graph, premisses):
    edges = []
    for color, edges_list in premisses.items():
        if len(edges_list) > 1:
            edges += edges_list

    (s1, t1), (s2, t2) = edges
    formula1 = graph.get_node_attribute(s1, ProofGraph.FORMULA)
    formula2 = graph.get_node_attribute(s2, ProofGraph.FORMULA)

    if len(formula1) > len(formula2):
        return (s2, t2), (s1, t1)
    else:
        return (s1, t1), (s2, t2)


def get_minor_premiss(graph, premisses):
    minor_premiss, major = get_minor_and_major_premiss(graph, premisses)
    return minor_premiss


def get_major_premiss(graph, premisses):
    minor, major_premiss = get_minor_and_major_premiss(graph, premisses)
    return major_premiss


def get_label_source(graph, (u, v)):
    formula = graph.get_node_attribute(u, ProofGraph.FORMULA)
    return formula


def get_single_premiss(premisses):
    edges = []
    for color, edges_list in premisses.items():
        if len(edges_list) > 1:
            edges += edges_list
    edge, = edges
    return edge


def raw_formula(formula):
    number_imp = formula.count(IMPLICATION)
    number_open_par = formula.count("(")

    if number_imp == number_open_par:
        return formula[1:-1]
    else:
        return formula


def get_antecedent(formula):
    formula = raw_formula(formula)

    if formula[0] != "(":
        formulas = formula.split(IMPLICATION)
        return formulas[0]
    else:
        open_p = 1
        close_p = 0
        index = 1
        while open_p != close_p:
            if formula[index] == "(":
                open_p += 1
            elif formula[index] == ")":
                close_p += 1
            index += 1
        return formula[1:index-1]


def get_consequent(formula):
    formula = raw_formula(formula)

    if formula[0] != "(":
        formulas = formula.split(IMPLICATION)
        return formulas[1]
    else:
        open_p = 1
        close_p = 0
        index = 1
        while open_p != close_p:
            if formula[index] == "(":
                open_p += 1
            elif formula[index] == ")":
                close_p += 1
            index += 1
        return formula[index+len(IMPLICATION)+1:-1]


def edges_target(edges, target):
    elected_edges = []
    for (s, t) in edges:
        if target == t:
            elected_edges.append((s, t))
    return elected_edges


def get_out_edge_color(graph, node, color):
    out_edges = graph.get_deductive_out_edges(node)
    out_edges_color = []

    for (u, v) in out_edges:
        edge_color = graph.get_edge_attribute(u, v, ProofGraph.COLOR)
        if color == edge_color:
            out_edges_color.append((u, v))

    return out_edges_color


# Mark nodes without incident edges as hypothesis
def mark_hypothesis(graph):
    for node in graph.get_nodes():
        deductive_in_degree = graph.get_deductive_in_degree(node)
        is_hypothesis = graph.get_node_attribute(node, ProofGraph.HYPOTHESIS)
        if deductive_in_degree == 0 and not is_hypothesis:
            graph.set_node_attribute(node, ProofGraph.HYPOTHESIS, True)


# Set color -1 to collapsed edges
def set_lambda_color(graph):
    for (source, target) in graph.get_edges():
        is_ancestor = graph.get_edge_attribute(source,
                                               target,
                                               ProofGraph.ANCESTOR)
        if not is_ancestor:
            is_collapsed = graph.get_edge_attribute(source,
                                                    target,
                                                    ProofGraph.COLLAPSED)
            if is_collapsed:
                graph.set_edge_attribute(source, target, ProofGraph.COLOR, -1)


class Error(Exception):

    def __init__(self, message):
        Exception.__init__(self, message)

    def __str__(self):
        return self.message


class InvalidException(Error):

    def __init__(self, message):
        Error.__init__(self, message)
