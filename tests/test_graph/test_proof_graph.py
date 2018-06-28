"""
Test for src/graph/proof_graph.py
"""

import unittest as unt
import networkx as nx
import src.exception as exc
from src.graph.proof_graph import ProofGraph
from src.graph.graph_adapter import GraphAdapter


class ProofGraphTest(unt.TestCase):

    def setUp(self):
        self.proof_graph = ProofGraph()

    def test_set_root(self):
        # Test graph with no root
        graph = nx.DiGraph()
        graph.add_node('1')
        graph.add_node('2')
        graph.add_edges_from([('1', '2'), ('2', '1')])
        self.proof_graph.set_graph(graph)
        self.assertRaises(
            exc.ProofGraphError,
            self.proof_graph.set_root
        )

        # Test graph with more than one root
        graph = nx.DiGraph()
        graph.add_node('1')
        graph.add_node('2')
        self.proof_graph.set_graph(graph)
        self.assertRaises(
            exc.ProofGraphError,
            self.proof_graph.set_root
        )

        # Test set root
        graph = nx.DiGraph()
        graph.add_node('1')
        graph.add_node('2')
        graph.add_edge('1', '2')
        self.proof_graph.set_graph(graph)
        self.assertEqual(self.proof_graph.root, '1')

    def test_set_graph(self):
        graph = nx.DiGraph()
        graph.add_node('1')
        graph.add_node('2')
        graph.add_edge('1', '2')

        # Test graph type
        self.proof_graph.set_graph(graph)
        self.assertIsInstance(self.proof_graph.graph, GraphAdapter)

    def test_load_dot(self):
        success_file = "input_test/input_success.dot"

        # Test graph type
        self.proof_graph.load_dot(success_file)
        self.assertIsInstance(self.proof_graph.graph, GraphAdapter)

    def test_set_node_attribute(self):
        graph = nx.DiGraph()

    def test_get_node_attribute(self):
        pass

    def test_get_all_node_attributes(self):
        pass

    def test_get_in_edges(self):
        pass

    def test_get_out_edges(self):
        pass

    def test_get_deductive_in_degree(self):
        pass

    def test_get_deductive_out_degree(self):
        pass

    def test_get_deductive_in_neighbors(self):
        pass

    def test_get_deductive_out_neighbors(self):
        pass

    def test_get_deductive_in_edges(self):
        pass

    def test_get_deductive_out_edges(self):
        pass

    def test_get_ancestor_in_edges(self):
        pass

    def test_get_ancestor_out_edges(self):
        pass

    def test_redirect_in_edges(self):
        pass

    def test_redirect_out_edges(self):
        pass

    def test_remove_node(self):
        pass

    def test_add_ancestor_edge(self):
        pass

    def test_add_collapsed_edge(self):
        pass

    def test_set_edge_attribute(self):
        pass

    def test_get_edge_attribute(self):
        pass

    def test_get_all_edge_attributes(self):
        pass

    def test_remove_edge(self):
        pass

    def test_remove_edges(self):
        pass

    def test_to_agraph(self):
        pass


if __name__ == '__main__':
    unt.main()