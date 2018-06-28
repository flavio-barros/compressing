#!/usr/local/bin/python
# coding: utf-8

from BitVector import BitVector
import src.exception as exc
import re
from src import exception, constants
from graph_adapter import GraphAdapter


class ProofGraph:
    """
    Base class for proof graphs.

    A ProofGraph is a directed graph that represents a derivation of
    natural deduction in the purely implicational fragment of minimal
    logic.

    A ProofGraph instance stores edge and node attributes to support
    the compression.

    Parameters
    ----------
    - file_path: path of DOT (graph description language) file that
        contains the proof graph.

    Nodes attributes
    ----------------
    - label: string of formula associated with node.
    - ancestor_target: boolean that informs if the node is the target
        of some ancestor edge.
    - hypothesis: boolean that informs if the node was marked as
        hypothesis during compression.

    Edges attributes
    ----------------
    - color: value of edge color. Initially, all edges have color 0.
    - ancestor: boolean that informs if the edge is of the ancestor
        type.

    Deductive edges attributes
    --------------------------
    - dependencies: bit vector (from BitVector class, see more:
        http://pypi.org/project/BitVector/) that stores the
        dependencies of each deductive edge.
    - collapsed: boolean that informs if the deductive edge was
        collapsed.

    Ancestor edges attributes
    -------------------------
    - path: list that stores the path associated with the ancestor
        edge.
    """

    LABEL = constants.LABEL
    FORMULA = constants.FORMULA
    ANCESTOR_TARGET = constants.ANCESTOR_TARGET
    DISCHARGE = constants.DISCHARGE
    COLOR = constants.DEDUCTIVE_COLOR
    ANCESTOR = constants.ANCESTOR
    PATH = constants.PATH
    HYPOTHESIS = constants.HYPOTHESIS
    DEPENDENCIES = constants.DEPENDENCIES
    COLLAPSED = constants.COLLAPSED

    NODE_ATTRIBUTES = [LABEL, FORMULA, ANCESTOR_TARGET, HYPOTHESIS, DISCHARGE]
    EDGE_ATTRIBUTES = [COLOR, ANCESTOR, PATH, DEPENDENCIES, COLLAPSED]

    def __init__(self, file_path=None, init_data=False):
        """
        Initializes an instance with the creation of the graph from a
        dot file.

        Edges and nodes attributes are added. In the beginning, only
        deductive edges are in the graph.

        For each subformula in the proof is attributed a index. All
        indexes are stored in dictionary-like object.

        For each deductive edge is calculated the bit vector of
        dependencies.

        Parameters
        ----------
        file_path: dot file
            File that contains a derivation of natural deduction.
            If file_path is None or the file does not exists, an
            exception are raised
        """
        self.graph = None
        self.root = None

        if file_path:
            self.load_dot(file_path)
            if init_data:
                self.init_proof_graph_data()

    def set_root(self):
        """
        Identifies the root of the derivation and stores it in the
        instance variable 'root'.

        The root is the conclusion of the proof and has no out edges.

        Raises
        ------
        ProofGraphError
            If root is not found
        """
        self.root = None
        for node in list(self.graph.get_nodes()):
            if self.graph.get_out_degree(node) == 0:
                if not self.root:
                    self.root = node
                else:
                    message = "The ProofGraph instance has many roots"
                    raise exception.ProofGraphError(message)

        if not self.root:
            message = "The ProofGraph instance has no root"
            raise exception.ProofGraphError(message)

    def set_graph(self, graph):
        """
        Set Digraph 'graph' to instance variable 'graph'
        """
        graph_adapter = GraphAdapter()
        graph_adapter.set_graph(graph)
        self.graph = graph_adapter

    def load_dot(self, file_path):
        """
        Create GraphAdapter instance from file and assign to instance
        variable 'graph'
        """
        graph_adapter = GraphAdapter()
        graph_adapter.load_dot(file_path)
        self.graph = graph_adapter

    # Not tested
    def init_proof_graph_data(self):
        self.set_root()
        self.__init_nodes_attributes()
        self.__set_formulas_indexes()
        self.__init_edges_attributes()
        self.__identify_discharged_ocurrences()
        self.__set_edges_dependencies(self.root)
        self.__set_nodes_level(self.root)

    # Not tested
    def __init_edges_attributes(self):
        """
        Initializes the edges attributes.

        Before the compression process, all the edges in the graph are
        deductives and have color 0.

        The bit vector of each edge has size equal to the number of
        subformulas in the proof.
        """
        qty_formulas = len(self.formulas_index)
        for (u, v) in self.graph.get_edges():
            self.graph.set_edge_attribute(u, v, ProofGraph.COLOR, 0)
            self.graph.set_edge_attribute(u, v, ProofGraph.ANCESTOR, False)
            self.graph.set_edge_attribute(u, v, ProofGraph.COLLAPSED, False)
            vector = BitVector(size=qty_formulas)
            self.graph.set_edge_attribute(u, v, ProofGraph.DEPENDENCIES, vector)

    # Not tested
    def __init_nodes_attributes(self):
        """
        Initialize nodes attributes.

        The 'ancestor_target' and 'hypothesis' are set true during the
        compression.
        """
        for node in list(self.graph.get_nodes()):
            self.graph.set_node_attribute(node, ProofGraph.ANCESTOR_TARGET,
                                          False)
            self.graph.set_node_attribute(node, ProofGraph.HYPOTHESIS, False)
            formula = self.__raw_formula(node)
            self.graph.set_node_attribute(node, ProofGraph.FORMULA, formula)

    # Not tested
    def __raw_formula(self, node):
        """
        Extracts only the corresponding formula from previous label
        node.

        Parameters
        ----------
        node: node
            Node in the graph
        """
        node_label = self.graph.get_node_attribute(node, ProofGraph.LABEL)

        if re.match(r'^\[(.*)\][0-9]+', node_label):
            match = re.search(r'^\[(.*)\][0-9]+[a-z]*$', node_label)
            return match.group(1)
        elif re.match(r'^(\(.*\)).[0-9]+', node_label):
            match = re.search(r'^(\(.*\)).[0-9]+[a-z]*$', node_label)
            return match.group(1)
        else:
            return node_label

    # Not tested
    def __set_formulas_indexes(self):
        """
        Stores each sub-formula in a dictionary-like object.

        Each sub-formula has only one key in the dict.
        """
        formulas_index = {}
        index = 0
        for node in list(self.graph.get_nodes()):
            formula = self.graph.get_node_attribute(node, ProofGraph.FORMULA)
            if not formulas_index.has_key(formula):
                formulas_index[formula] = index
                index += 1
        self.formulas_index = formulas_index

    # Not tested
    def __set_edges_dependencies(self, node):
        """
        Calculate the dependencies of the edges pointing out of the
        node.

        The edge dependencies are only calculated if all previous
        dependencies have already been computed.

        If not all previous dependencies have been computed, a
        recursive call is performed for immediately preceding edges.

        Note
        ----
        The dependencies are computed only for subtree rooted in the
        parameter 'node' of the first call.

        Parameters
        ----------
        node: node
            Node in the graph
        """
        in_degree = self.graph.get_in_degree(node)
        if in_degree == 0:
            out_neighbor, = self.graph.get_out_neighbors(node)
            formula = self.graph.get_node_attribute(out_neighbor,
                                                    ProofGraph.FORMULA)
            index = self.formulas_index[formula]
            dependencies = self.graph.get_edge_attribute(node, out_neighbor,
                                                         ProofGraph.DEPENDENCIES)
            dependencies[index] = 1
        elif in_degree == 1:
            in_neighbor, = self.graph.get_in_neighbors(node)
            self.__set_edges_dependencies(in_neighbor)
            discharged_formula = self.graph.get_node_attribute(
                node, ProofGraph.DISCHARGE)
            index = self.formulas_index[discharged_formula]
            out_neighbor, = self.graph.get_out_neighbors(node)
            dependencies = self.graph.get_edge_attribute(node,
                                                         out_neighbor,
                                                         ProofGraph.DEPENDENCIES)
            dependencies[index] = 0
        elif in_degree == 2:
            in_neighbor_1, in_neighbor_2 = self.graph.get_in_neighbors(node)
            self.__set_edges_dependencies(in_neighbor_1)
            self.__set_edges_dependencies(in_neighbor_2)
            if self.graph.get_out_degree(node) > 0:
                dependencies_1 = self.graph.get_edge_attribute(
                    in_neighbor_1, node, ProofGraph.DEPENDENCIES)
                dependencies_2 = self.graph.get_edge_attribute(
                    in_neighbor_2, node, ProofGraph.DEPENDENCIES)
                out_neighbor, = self.graph.get_out_neighbors(node)
                dependencies = self.graph.get_edge_attribute(
                    node, out_neighbor, ProofGraph.DEPENDENCIES)
                dependencies = dependencies_1 ^ dependencies_2

    # Not tested
    def __identify_discharged_ocurrences(self):
        """
        Identifies and stores which formulas were discharged in the
        'implication introduction' rules.
        """
        discharged_occurrences = dict()
        conclusions = dict()
        for node in self.graph.get_nodes():
            label = self.graph.get_node_attribute(node, ProofGraph.LABEL)
            formula = self.graph.get_node_attribute(node, ProofGraph.FORMULA)
            if re.match(r'\[.+\][0-9]+', label):
                match = re.search(r'\[.+\]([0-9][0-9a-z]*)', label)
                if not discharged_occurrences.has_key(match.group(1)):
                    discharged_occurrences[match.group(1)] = formula
            if re.match(r'.+[\s]([0-9][0-9a-z]*)', label):
                match = re.match(r'.+[\s]([0-9][0-9a-z]*)', label)
                if not conclusions.has_key(match.group(1)):
                    conclusions[match.group(1)] = node
                else:
                    pass
                    # raise exception here
        for key, node in conclusions.items():
            discharged_occurrence = discharged_occurrences[key]
            self.graph.set_node_attribute(node, ProofGraph.DISCHARGE,
                                          discharged_occurrence)

    # Not tested
    def __set_nodes_level(self, root):
        """
        Build a dictionary-like object that groups the nodes according
        to the derivation level.

        Parameters
        ----------
        root: node
            Node in the graph. Derivation root.
        """
        level = 0
        nodes_level = {level: [root]}
        while nodes_level[level]:
            nodes_level[level + 1] = []
            for node in nodes_level[level]:
                in_neighbors = list(self.graph.get_in_neighbors(node))
                for in_neighbor in in_neighbors:
                    if in_neighbor not in nodes_level[level + 1]:
                        nodes_level[level + 1].append(in_neighbor)
            level += 1
        self.nodes_level = nodes_level

    def set_node_attribute(self, node, attribute, value):
        """
        Set attribute to the node.

        Parameters
        ----------
        node: node
            Node in the graph

        attribute: node attribute, see ProofGraph.NODE_ATTRIBUTES
            Attribute of the node

        value: string, int or boolean
            Value of the node attribute

        Raises
        ------
        NodeProofGraphError
            The node is not in the graph

        NodeAttributeProofGraphError
            The attribute is invalid
        """
        if attribute in ProofGraph.NODE_ATTRIBUTES:
            try:
                self.graph.set_node_attribute(node, attribute, value)
            except exc.NodeGraphError:
                message = "not exists in proof graph"
                raise exc.NodeProofGraphError(node, message)
        else:
            message = "is invalid"
            raise exc.NodeAttributeProofGraphError(attribute, message)

    def get_node_attribute(self, node, attribute):
        """
        Return' node attribute.

        Parameters
        ----------
        node: node
            Node in the graph

        attribute: string
            Attribute of the node

        Raises
        ------
        ProofGraphError
            The node is not in the graph

        Returns
        -------
        attribute
            Node attribute or None if node is not in the graph.
        """

        return self.graph.get_node_attribute(node, attribute)

    def get_all_node_attributes(self, node):
        """
        Return all node attributes

        Parameters
        ----------
        node: node
            Node in the graph

        Raises
        ------
        ProofGraphError
            The node is not in the graph

        Returns
        -------
        attributes: List
            List of node attributes or None if node is not in the
            graph.
        """
        return self.graph.get_all_node_attributes(node)

    def get_in_edges(self, node):
        """
        Return the edges that pointing to the node.

        Parameters
        ----------
        node: node
            Node in the graph

        Raises
        ------
        ProofGraphError
            The node is not in the graph

        Returns
        -------
        in_edges: List
            List of edges (source, target) that pointing to the node.
        """
        return self.graph.get_in_edges(node)

    def get_out_edges(self, node):
        """
        Return the edges that pointing out of the node.

        Parameters
        ----------
        node: node
            Node in the graph

        Raises
        ------
        ProofGraphError
            The node is not in the graph

        Returns
        -------
        out_edges: List
            List of edges (source, target) that pointing out of the
            node.
        """
        return self.graph.get_out_edges(node)

    def get_deductive_in_degree(self, node):
        """
        Return node deductive_in_degree

        The deductive_in_degree is the number of deductive edges
        pointing to the node.

        Parameters
        ----------
        node: node
            Node in the graph

        Raises
        ------
        ProofGraphError
            The node is not in the graph

        Returns
        -------
        deductive_in_degree: int
            number of deductive edges pointing to the node.
        """
        count_deductive_edges = 0
        for (source, target) in self.graph.get_in_edges(node):
            is_ancestor = self.graph.get_edge_attribute(source, target,
                                                        ProofGraph.ANCESTOR)
            if not is_ancestor:
                count_deductive_edges += 1
        return count_deductive_edges

    def get_deductive_out_degree(self, node):
        """
        Return node deductive_out_degree

        The deductivce_out_degree is the number of deductive edges
        pointing out of the node.

        Parameters
        ----------
        node: node
            Node in the graph

        Raises
        ------
        ProofGraphError
            The node is not in the graph

        Returns
        -------
        deductive_out_degree: int
            number of deductive edges pointing out of the node.
        """
        count_deductive_edges = 0
        for (source, target) in self.graph.get_out_edges(node):
            is_ancestor = self.graph.get_edge_attribute(source, target,
                                                        ProofGraph.ANCESTOR)
            if not is_ancestor:
                count_deductive_edges += 1
        return count_deductive_edges

    def get_deductive_in_neighbors(self, node):
        """
        Return the nodes that are source of deductives edges that
        pointing to the node.

        Parameters
        ----------
        node: node
            Node in the graph

        Raises
        ------
        ProofGraphError
            The node is not in the graph

        Returns
        -------
        deductive_in_neighbors: List
            List of nodes that are sources of deductives edges that
            pointing out of the node.
        """
        in_neighbors = []
        for (source, target) in self.graph.get_in_edges(node):
            is_ancestor = self.graph.get_edge_attribute(source, target,
                                                        ProofGraph.ANCESTOR)
            if not is_ancestor:
                in_neighbors.append(source)
        return in_neighbors

    def get_deductive_out_neighbors(self, node):
        """
        Return the nodes that are targets of deductives edges that
        pointing out of the node.

        Parameters
        ----------
        node: node
            Node in the graph

        Raises
        ------
        ProofGraphError
            The node is not in the graph

        Returns
        -------
        deductive_out_neighbors: List
            List of nodes that are targets of deductives edges that
            pointing out of the node.
        """
        out_neighbors = []
        for (source, target) in self.graph.get_out_edges(node):
            is_ancestor = self.graph.get_edge_attribute(source, target,
                                                        ProofGraph.ANCESTOR)
            if not is_ancestor:
                out_neighbors.append(target)
        return out_neighbors

    def get_deductive_in_edges(self, node):
        """
        Return the deductive edges that pointing to the node.

        Parameters
        ----------
        node: node
            Node in the graph

        Raises
        ------
        ProofGraphError
            The node is not in the graph

        Returns
        -------
        deductive_in_edges: List
            List of deductive edges (souce, target) that pointing to the node.
        """
        in_deductive_edges = []
        for (source, target) in self.graph.get_in_edges(node):
            is_ancestor = self.graph.get_edge_attribute(source, target,
                                                        ProofGraph.ANCESTOR)
            if not is_ancestor:
                in_deductive_edges.append((source, target))
        return in_deductive_edges

    def get_deductive_out_edges(self, node):
        """
        Return the deductive edges that pointing out of the node.

        Parameters
        ----------
        node: node
            Node in the graph

        Raises
        ------
        ProofGraphError
            The node is not in the graph

        Returns
        -------
        deductive_out_edges: List
            List of deductive edges (source, target) that pointing out of the
            node.
        """
        out_deductive_edges = []
        for (source, target) in self.graph.get_out_edges(node):
            is_ancestor = self.graph.get_edge_attribute(source, target,
                                                        ProofGraph.ANCESTOR)
            if not is_ancestor:
                out_deductive_edges.append((source, target))
        return out_deductive_edges

    def get_ancestor_in_edges(self, node):
        """
        Return the ancestor edges that pointing to the node.

        Parameters
        ----------
        node: node
            Node in the graph

        Raises
        ------
        ProofGraphError
            The node is not in the graph

        Returns
        -------
        ancestor_in_edges: List
            List of ancestor edges (source, target) that pointing to the node.
        """
        in_ancestor_edges = []
        for (source, target) in self.graph.get_in_edges(node):
            is_ancestor = self.graph.get_edge_attribute(source, target,
                                                        ProofGraph.ANCESTOR)
            if is_ancestor:
                in_ancestor_edges.append((source, target))
        return in_ancestor_edges

    def get_ancestor_out_edges(self, node):
        """
        Return the ancestor edges that pointing out of the node.

        Parameters
        ----------
        node: node
            Node in the graph

        Raises
        ------
        ProofGraphError
            The node is not in the graph

        Returns
        -------
        ancestor_out_edges: List
            List of ancestor edges (souce, target) that pointing out of the
            node.
        """
        out_ancestor_edges = []
        for (source, target) in self.graph.get_out_edges(node):
            is_ancestor = self.graph.get_edge_attribute(source, target,
                                                        ProofGraph.ANCESTOR)
            if is_ancestor:
                out_ancestor_edges.append((source, target))
        return out_ancestor_edges

    def redirect_in_edges(self, node_u, node_v, **kwargs):
        """
        Redirect edges that pointing to the node_u to node_v.

        Remove edges that have node_u as target and add edges with same
        source and attributes pointing to the node_v.

        Parameters
        ----------
        node_u, node_v: node
            Nodes in the graph

        kwargs: keywords arguments, optional
            Only one argument is considered, 'ancestor_edges'.
            If 'ancestor_edges' is given, ancestor edges are considered
            in redirecting.

        """
        ancestor_edges = kwargs.get("ancestor_edges", None)
        if ancestor_edges:
            in_edges_u = self.graph.get_in_edges(node_u)
        else:
            in_edges_u = self.get_deductive_in_edges(node_u)
        for (source, target) in in_edges_u:
            attributes = self.get_all_edge_attributes(source, target)
            self.graph.add_edge(source, node_v, **attributes)
        self.graph.remove_edges(in_edges_u)

    def redirect_out_edges(self, node_u, node_v):
        """
        Redirect edges that pointing out the node_u to node_v.

        Remove edges that have node_u as source and add edges with same
        target and attributes pointing out of the node_v.

        Parameters
        ----------
        node_u, node_v: node
            Nodes in the graph
        """
        out_edges_u = self.get_deductive_out_edges(node_u)
        for (source, target) in out_edges_u:
            edge_attributes = self.graph.get_all_edge_attributes(source, target)
            self.graph.add_edge(node_v, target, **edge_attributes)
        self.graph.remove_edges(out_edges_u)

    def remove_node(self, node):
        """
        Remove node from the graph.

        Parameters
        ----------
        node: node
            Node in the graph

        Raises
        ------
        ProofGraphError
            The node is not in the graph
        """
        self.graph.remove_node(node)

    def add_ancestor_edge(self, source, target, **kwargs):
        """
        Add ancestor edge between source and target.

        Parameters
        ----------
        source, target: node
            Nodes in the graph

        kwargs: keywords arguments, optional
            Two arguments are considered, 'path' and 'new_color'.
            If 'path' and 'new_color' are given, the ancestor edge is
            added with 'new_color' at the beginning of 'path'.
            If 'path' is given, the ancestor edge is added with this
            path as attribute.
            If 'new_color' is given, the ancestor edge is added with
            the path containing only 'new_color'.
            If neither argument is given, the ancestor edge is added
            with empty path.

        Raises
        ------
        ProofGraphError:
            If there is not an edge between source and target.
        """
        path = kwargs.get("path", None)
        new_color = kwargs.get("new_color", None)
        if path and new_color:
            new_path = list(path)
            new_path.insert(0, new_color)
            self.graph.add_edge(source, target, ancestor=True, path=new_path)
        elif new_color:
            new_path = list()
            new_path.append(new_color)
            self.graph.add_edge(source, target, ancestor=True, path=new_path)
        elif path:
            self.graph.add_edge(source, target, ancestor=True, path=path)

    def add_collapsed_edge(self, node_u, node_v, target):
        """
        Add a deductive coll edge between node_u and target.

        There must be an deductive edge between node_u and target, and
        between node_v and target.

        Both edges are removed, and is added an edge between node_u and
        target with only 'collapsed' attribute set to True.

        Parameters
        ----------
        node_u, node_v, target: node
            Nodes in the graph
        """
        self.graph.remove_edge(node_u, target)
        self.graph.remove_edge(node_v, target)
        attributes = {ProofGraph.COLLAPSED: True}
        self.graph.add_edge(node_u, target, **attributes)

    def set_edge_attribute(self, source, target, attribute, value):
        """
        Set attribute to the edge.

        Parameters
        ----------
        source, target: node
            Nodes in the graph

        attribute: string
            Attribute of the edge between source and target

        value: boolean or list
            Value of the edge attribute

        Raises
        ------
        ProofGraphError:
            If there is not an edge between source and target.
        """
        self.graph.set_edge_attribute(source, target, attribute, value)

    def get_edge_attribute(self, source, target, attribute):
        """
        Return the attribute of the edge between source and target.

        Parameters
        ----------
        source, target: node
            Nodes in the graph

        attribute: string
            Attribute of the edge between source and target

        Raises
        ------
        ProofGraphError:
            If there is not an edge between source and target.

        Returns
        -------
        attribute: string, int or boolean
            Edge attribute or None if attribute is not valid.

        """
        return self.graph.get_edge_attribute(source, target, attribute)

    def get_all_edge_attributes(self, source, target):
        """
        Return all attributes of the edge between source and target.

        Parameters
        ----------
        source, target: node
            Nodes in the graph

        Raises
        ------
        ProofGraphError:
            If there is not an edge between source and target.

        Returns
        -------
        attributes: List
            List of attributes of the edge between source and target.
        """
        return self.graph.get_all_edge_attributes(source, target)

    def remove_edge(self, source, target):
        """
        Remove edge between source and target.

        Parameters
        ----------
        source, target: node
            Node in the graph

        Raises
        ------
        ProofGraphError
            If there is not an edge between source and target.
        """
        self.graph.remove_edge(source, target)

    def remove_edges(self, edges):
        """
        Remove all edges in 'edges'

        Parameters
        ----------
        edges: List
            List of edges (source, target)
        """
        self.graph.remove_edges(edges)

    def to_agraph(self):
        """
        Return a Agraph instance from Digraph instance (PyGraphviz from
        Networkx)
        """
        return self.graph.to_agraph()
