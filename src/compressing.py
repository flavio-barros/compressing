#!/usr/local/bin/python
# coding: utf-8

import argparse
from graph import proof_graph as prg
import compression as cmp
from visualize import visual_proof_graph as vpg


# from visual_graph_adapter import VisualGraphAdapter

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=file, help="read proof graph from file")
    args = parser.parse_args()

    proof_graph = prg.ProofGraph(file_path=args.file, init_data=True)

    visual_proof_graph = vpg.VisualProofGraph(proof_graph)

    visual_proof_graph.draw_input()

    nodes_repeated_formulas = cmp.get_nodes_repeated_formulas(proof_graph)

    print "Starting... "

    for nodes in nodes_repeated_formulas:
        node_u = nodes.pop()
        for node_v in nodes:
            rule_function = cmp.identify_rule(proof_graph, node_u, node_v)
            node_u = cmp.exec_rule(rule_function, proof_graph, node_u, node_v)

    print "done."

    visual_proof_graph.draw_final()


if __name__ == '__main__':
    main()
