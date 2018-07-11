#!/usr/local/bin/python
# coding: utf-8

import argparse

from compression import compression
from graph import proof_graph as pgr
from visualize import visual_proof_graph as vpg


def main():

    parser = argparse.ArgumentParser()

    # file argument
    parser.add_argument("file", type=file,
                        help="read proof graph from file")

    # visualize argument
    parser.add_argument("--visualize", dest='visualize', action='store_true',
                        help="generates pdf visualization")
    parser.add_argument("--no-visualize", dest='visualize',
                        action='store_false',
                        help="not generates pdf visualization")
    parser.set_defaults(visualize=True)

    args = parser.parse_args()

    proof_graph = pgr.ProofGraph(file_path=args.file, init_data=True)

    visual_proof_graph = vpg.VisualProofGraph(proof_graph)

    if args.visualize:
        visual_proof_graph.draw_input()

    print "Starting compressing"

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

    print "Compression done"

    if args.visualize:
        print "Generating PDF files"
        visual_proof_graph.draw_final()


if __name__ == '__main__':
    main()
