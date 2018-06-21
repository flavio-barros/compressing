def remove_discharging_edges(graph):
	build_dependencies_structure(graph)

	root = graph.graph["root"]
	build_dependencies(graph, root)

	remove_edges(graph)

def build_dependencies_structure(graph):
	ordered_formulas = {}
	seq = 0
	for node in nx.nodes(graph):
		node_attr = graph.nodes[node]
		formula = node_attr["formula"]
		if not ordered_formulas.has_key(formula):
			ordered_formulas[formula] = seq
			seq+=1

	graph.graph["ordered_formulas"] = ordered_formulas

	for (u, v, data) in graph.edges(data=True):
		data["dependencies"] = bv.BitVector(size = len(ordered_formulas))
