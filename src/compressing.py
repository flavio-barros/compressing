#!/usr/local/bin/python
# coding: utf-8

import argparse

from src.graph import proof_graph as prg
from src.compression import compression
from src.visualize import visual_proof_graph as vpg


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=file, help="read proof graph from file")
    args = parser.parse_args()

    proof_graph = prg.ProofGraph(file_path=args.file, init_data=True)

    visual_proof_graph = vpg.VisualProofGraph(proof_graph)

    visual_proof_graph.draw_input()

    nodes_repeated_formulas = \
        compression.get_nodes_repeated_formulas(proof_graph)

    for nodes in nodes_repeated_formulas:
        node_u = nodes.pop()
        for node_v in nodes:
            rule_function = compression.identify_rule(proof_graph,
                                                      node_u,
                                                      node_v)
            node_u = compression.exec_rule(rule_function,
                                           proof_graph,
                                           node_u,
                                           node_v)

    print "done."

    visual_proof_graph.draw_final()


if __name__ == '__main__':
    main()
