import networkx as nx

def main():
    file_path = "input/input_test.dot"
    grafo = nx.DiGraph(nx.nx_agraph.read_dot(file_path))

    grafo_prova  = nx.DiGraph()
    index = 0
    for node in list(grafo.nodes):
        grafo_prova.add_node(index, label=node)
        index+=1

    for node in list(grafo_prova.nodes):
        # print node, grafo_prova.nodes[node]
        pass

    agraph = nx.nx_agraph.to_agraph(grafo)
    file_path = "pdf/"+"TESTE"+".pdf"
    agraph.draw(file_path, prog="dot")


def rename_nodes(graph):
	pass

if __name__ == '__main__':
	main()
