#!/usr/local/bin/python
# coding: utf-8

import pygraphviz as pg
import graphviz as gv
import networkx as nx
import threading
import Queue as q
import multiprocessing

graph_queue = q.Queue()

def start_pdf_generator(graph_before, graph_after, rule_name, seq_collapse, collapsed_nodes):
	graph_before.graph["label"] = "collapse_"+str(seq_collapse)+"-"+rule_name+"-before"
	graph_after.graph["label"] = "collapse_"+str(seq_collapse)+"-"+rule_name+"-after"
	graph_before.graph["collapsed_nodes"] = collapsed_nodes
	graph_after.graph["collapsed_nodes"] = [collapsed_nodes[0]]

	global graph_queue
	graph_queue.put((graph_before, graph_after))

def wait_pdf_generator():
	graph_queue.join()

def create_pdf_generator_threads():
	for i in range(1):#multiprocessing.cpu_count()):
		t = threading.Thread(target=generate_collapse_pdf)
		t.daemon = True
		t.start()

def generate_comparison_pdf(graph_before, graph_after):
	# print "imprimindo 'before_graph'"
	graph_before.graph["label"] = "input"
	save_file_graph(graph_before)

	# print "imprimindo 'after_graph'"
	graph_after.graph["label"] = "compressed"
	save_file_graph(graph_after)
	merge_graphs(graph_before, graph_after, 10000)

	# print "imprimindo 'comparison_graph'"
	graph_before.graph["label"] = "comparison_graph"
	save_file_graph(graph_before)

def generate_collapse_pdf():
	global graph_queue
	while True:
		collapse_data = graph_queue.get()
		graph_before, graph_after = collapse_data

		# print "BEFORE"
		subgraph_before = get_subgraph_collapse_before(graph_before)

		# print "AFTER"
		subgraph_after = get_collapse_subgraph_after(subgraph_before, graph_after)

		subgraph_before.graph["label"] = graph_before.graph["label"]
		subgraph_after.graph["label"] = graph_after.graph["label"]
		subgraph_before.graph["collapsed_nodes"] = graph_before.graph["collapsed_nodes"]
		subgraph_after.graph["collapsed_nodes"] = graph_after.graph["collapsed_nodes"]

		t1 = threading.Thread(target=save_file_subgraph, args=(subgraph_before,))
		t1.start()

		t2 = threading.Thread(target=save_file_subgraph, args=(subgraph_after,))
		t2.start()

		graph_queue.task_done()

def document_graph(graph, graph_name):
	graph_copy = graph.copy()
	graph_copy.graph["label"] = graph_name

	t = threading.Thread(target=save_file_graph, args=(graph_copy,))
	t.start()

def save_file_subgraph(graph):
	rename_attributes(graph)
	agraph = nx.nx_agraph.to_agraph(graph)
	set_rank_nodes_subgraph(graph, agraph)
	file_path = "pdf/"+graph.graph["label"]+".pdf"
	agraph.draw(file_path, prog="dot")

def save_file_graph(graph):
	rename_attributes(graph)
	agraph = nx.nx_agraph.to_agraph(graph)
	file_path = "pdf/"+graph.graph["label"]+".pdf"
	agraph.draw(file_path, prog="dot")

def get_subgraph_collapse_before(graph):
	subgraph = nx.DiGraph()

	paths_list = []

	for node in graph.graph["collapsed_nodes"]:
		add_copy_node(graph, subgraph, node)
		for (source_in, target_in, data_in) in graph.in_edges(node, data=True):
			add_copy_node(graph, subgraph, source_in)
			if data_in["ancestor"]:
				add_copy_ancestor_edge(graph, subgraph, (source_in, target_in))

				all_paths = nx.all_simple_paths(graph, source=node, target=source_in)
				paths_list.append((all_paths, data_in["path"]))
			else:
				add_copy_deductive_edge(graph, subgraph, (source_in, target_in))
			if graph.nodes[source_in]["ancestor_target"]:
				for (source_in_in, target_in_in, data_in_in) in graph.in_edges(source_in, data=True):
					if data_in_in["ancestor"]:
						add_copy_node(graph, subgraph, source_in_in)
						add_copy_ancestor_edge(graph, subgraph, (source_in_in, target_in_in))

						all_paths = nx.all_simple_paths(graph, source=node, target=source_in_in)
						paths_list.append((all_paths, data_in_in["path"]))
		for (source_out, target_out, data_out) in graph.out_edges(node, data=True):
			add_copy_node(graph, subgraph, target_out)
			add_copy_deductive_edge(graph, subgraph, (source_out, target_out))

	for (paths, edge_path) in paths_list:
		paths = list(paths)
		print str(len(paths))+" encontrados"
		print
		add_paths(graph, subgraph, paths, edge_path)

	return subgraph

def get_collapse_subgraph_after(subgraph_before, graph_after):
	subgraph_after = nx.DiGraph()

	for node in list(subgraph_before.nodes):
		if graph_after.has_node(node):
			add_copy_node(graph_after, subgraph_after, node)

	for source in list(subgraph_after.nodes):
		for target in list(subgraph_after.nodes):
			if subgraph_before.has_edge(source, target):
				edge_data = subgraph_before.get_edge_data(source, target)
				if edge_data.has_key("composed"):
					add_copy_composed_edge(subgraph_before, subgraph_after, (source, target))
			if graph_after.has_edge(source, target):
				edge_data = graph_after.get_edge_data(source, target)
				if edge_data["ancestor"]:
					add_copy_ancestor_edge(graph_after, subgraph_after, (source, target))
				else:
					add_copy_deductive_edge(graph_after, subgraph_after, (source, target))

	return subgraph_after

def add_paths(graph, subgraph, paths, edge_path):
	for path in paths:
		# print ""
		# print "PATH: "+str(path)
		if not contains_ancestor_edges(graph, path):
			filtered_nodes, filtered_colors = filter_nodes_colored_edges_path(graph, path)
			if is_match_paths(filtered_colors, edge_path):
				add_composed_path(graph, subgraph, filtered_nodes, filtered_colors)

def contains_ancestor_edges(graph, path):
	max_index = len(path)-1
	index = 0
	while index < max_index:
		# print graph.has_edge(path[index], path[index+1])
		# print "CONTAINS A_E: ", path[index], path[index+1]
		# print str(graph.edges[path[index], path[index+1]])
		edge_data = graph.get_edge_data(path[index], path[index+1])
		if edge_data.has_key("ancestor") and edge_data["ancestor"]:
			return True
		index+=1
	return False

def filter_nodes_colored_edges_path(graph, path):
	filtered_nodes = []
	filtered_colors = []
	max_index = len(path)-1
	index = 1
	filtered_nodes.append(path[index])
	while index < max_index:
		node, next_node = path[index], path[index+1]
		edge_data = graph.get_edge_data(node, next_node)
		if edge_data["dependencies"] and edge_data["color"] > 0:
			filtered_nodes.append(next_node)
			filtered_colors.append(edge_data["color"])
			edge_source = next_node
		index+=1
	return filtered_nodes, filtered_colors

def is_match_paths(nodes_composed_path, edge_path):
	index_composed = len(nodes_composed_path)-1

	nodes_edge_path = edge_path.split(";")
	index_edge = len(nodes_edge_path)-1

	# print nodes_edge_path, nodes_composed_path

	while index_composed >= 0 and index_edge >= 0:
		if not nodes_composed_path[index_composed] == nodes_edge_path[index_edge]:
			return False
		index_composed-=1
		index_edge-=1
	return True

def add_composed_path(subgraph, graph, nodes, colors):
	max_index = len(nodes)-1
	index = 0
	print "ADD_PATH", nodes, colors
	while index < max_index:
		if not subgraph.has_node(nodes[index]):
			add_copy_node(graph, subgraph, nodes[index])
		if not subgraph.has_node(nodes[index+1]):
			add_copy_node(graph, subgraph, nodes[index+1])
		if subgraph.has_edge(nodes[index], nodes[index+1]):
			print "Editing edge", nodes[index], nodes[index+1]
			subgraph.edges[nodes[index], nodes[index+1]]["color"] = colors[index]
			subgraph.edges[nodes[index], nodes[index+1]]["style"] = "dashed"
			subgraph.edges[nodes[index], nodes[index+1]]["composed"] = True
		else:
			print "Adding edge", nodes[index], nodes[index+1]
			subgraph.add_edge(nodes[index], nodes[index+1], color=colors[index], style="dashed", composed=True)
		index+=1
	print ""

def add_copy_node(graph1, graph2, node, **kwargs):
	multi = kwargs.get("multi", None)

	formula = graph1.nodes[node]["formula"]
	ancestor_target = graph1.nodes[node]["ancestor_target"]
	hypothesis = graph1.nodes[node]["hypothesis"]

	if multi:
		graph2.add_node(multi*int(node), formula=formula, ancestor_target=ancestor_target, hypothesis=hypothesis)
	else:
		graph2.add_node(node, formula=formula, ancestor_target=ancestor_target, hypothesis=hypothesis)

def add_copy_deductive_edge(graph1, graph2, (source, target), **kwargs):
	multi = kwargs.get("multi", None)

	color = graph1.edges[source, target]["color"]
	dependencies = graph1.edges[source, target]["dependencies"]
	collapsed = graph1.edges[source, target]["collapsed"]

	if multi:
		graph2.add_edge(multi*int(source), multi*int(target), ancestor=False, color=color, dependencies=dependencies, collapsed=collapsed)
	else:
		graph2.add_edge(source, target, ancestor=False, color=color, dependencies=dependencies, collapsed=collapsed)

def add_copy_ancestor_edge(graph1, graph2, (source, target), **kwargs):
	multi = kwargs.get("multi", None)

	path = graph1.edges[source, target]["path"]

	if multi:
		graph2.add_edge(multi*int(source), multi*int(target), ancestor=True, path=path)
	else:
		graph2.add_edge(source, target, ancestor=True, path=path)

def add_copy_composed_edge(graph1, graph2, (source, target)):
	color = graph1.edges[source, target]["color"]
	style = graph1.edges[source, target]["style"]
	graph2.add_edge(source, target, color=color, style=style, composed=True, ancestor=False)

def rename_attributes(graph):
	for node in list(graph.nodes):
		graph.nodes[node]["label"] = graph.nodes[node]["formula"]
		if graph.nodes[node]["hypothesis"]:
			graph.nodes[node]["xlabel"] = "h"
			graph.nodes[node]["color"] = "red"

	for (u, v, data) in list(graph.edges(data=True)):
		if data.has_key("composed"):
			data["xlabel"] = str(data["color"])
			data["color"] = ""
		elif data["ancestor"]:
			data["xlabel"] = data["path"]
			data["color"] = "blue"
			data["fontcolor"] = "red"
		else:
			if data["collapsed"]:
				data["xlabel"] =  "<&#955;>"
			else:
				data["xlabel"] = str(data["color"])
				data["dependecies"] = ""
			data["color"] = ""

	if graph.graph.has_key("collapsed_nodes"):
		for node in graph.graph["collapsed_nodes"]:
			graph.nodes[node]["style"] = "filled"
			graph.nodes[node]["fillcolor"] = "grey"

def set_rank_nodes_subgraph(graph, agraph):
	in_nodes = []
	collapsed_nodes = graph.graph["collapsed_nodes"]
	out_nodes = []
	ancestor_source_nodes = []
	for node in collapsed_nodes:
		for (source_in, target_in, data_in) in graph.in_edges(node, data=True):
			if data_in["ancestor"]:
				ancestor_source_nodes.append(source_in)
			else:
				in_nodes.append(source_in)
				for (source_in_in, target_in_in, data_in_in) in graph.in_edges(source_in, data=True):
					if data_in_in["ancestor"]:
						ancestor_source_nodes.append(source_in_in)
		for (source_out, target_out, data_out) in graph.out_edges(node, data=True):
			out_nodes.append(target_out)
			if graph.nodes[target_out]["ancestor_target"]:
				for (source_in_out, target_in_out, data_in_out) in graph.in_edges(target_out, data=True):
					if data_in_out["ancestor"]:
						ancestor_source_nodes.append(source_in_out)
	out_nodes = list(set(out_nodes)-set(ancestor_source_nodes))

	if in_nodes:
		agraph.add_subgraph(in_nodes, rank='source')
		agraph.add_subgraph(collapsed_nodes, rank='same')
	else:
		agraph.add_subgraph(collapsed_nodes, rank='source')

	if ancestor_source_nodes:
		agraph.add_subgraph(ancestor_source_nodes, rank='sink')
		agraph.add_subgraph(out_nodes, rank='same')
	else:
		agraph.add_subgraph(out_nodes, rank='sink')

def set_rank_nodes_graph(graph, agraph):
	root = graph.graph["root"]
	agraph.add_subgraph(list(root), rank="sink")

	level_nodes = []
	level_nodes.append(root)

	for node in level_nodes:
		next_level_nodes = []
		for (source_in, target_in, data_in) in graph.in_edges(node, data=True):
			if not data_in["ancestor"] and not node in next_level_nodes:
				next_level_nodes.append(source_in)
		agraph.add_subgraph(next_level_nodes, rank="same")
		level_nodes = next_level_nodes

def remove_ancestor_edges(graph):
	for (source, target, data) in list(graph.edges(data=True)):
		if data["ancestor"]:
			graph.remove_edge(source, target)

def merge_graphs(graph1, graph2, multi):
	for node in list(graph2.nodes):
		add_copy_node(graph2, graph1, node, multi=multi)
	for (source, target, data) in list(graph2.edges(data=True)):
		if data["ancestor"]:
			add_copy_ancestor_edge(graph2, graph1, (source, target), multi=multi)
		else:
			add_copy_deductive_edge(graph2, graph1, (source, target), multi=multi)
