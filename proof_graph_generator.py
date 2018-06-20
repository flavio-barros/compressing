#!/usr/local/bin/python
# coding: utf-8

import pydotplus as pd
import graph_tool.all as gt

def inicia():

	global e_in
	global e_out
	global seqnode
	global Max

	grafoteste = pd.Graph()
	grafoteste.set_name("EntreNiveisVersion3Compressing33G3")

	descarte_counter=1
	est={}
	seqnode=1
	vis=set([])
	hg=(vis,grafoteste)

	for v in nos:
		novo_est={}
		hg[0].add(((1,v),descarte_counter))
		(hg,novo_est,descarte_counter)=constroi_ramo(novo_est,2,hg[1], hg[0],v,descarte_counter+1)
		hg=destroi_visitados_ref_nivel(hg,1,v,descarte_counter)
		est[(1,v)]=hg[1].root
		descarte_counter=descarte_counter+1

	hg=constroi_grafo_disjuntivo(hg,0,"basis",est)

	return grafoteste, e_in, e_out, seqnode

def constroi_ramo(est,k, grafo, visitados_hips, w,descarte_counter):
# Build and return the derivation of the absurdity (q) that a partial cycle having the (k-1)th visited node as w and descarte_counter and
# is the label that discharges the next step assumption, namely, in the k-th visited node in the whole derivation yet to be constructed
	global seqnode
	hg=(visitados_hips, grafo)

	vw=vertex_name(w)
	novo_est={}
	this_context_descarte_counter=descarte_counter-1

	if k < (Max+1):
		visitados=set([])
		for ((i,v),n) in visitados_hips:
			visitados.add(v)

		proibidos={v for v in nos if not linked(g,vw,v) and not linked(g,v,vw)}

		for v in nos:
			if v in visitados:
				i=get_k(v,visitados_hips)
				n_descarte=get_descarte(v,visitados_hips)
				hg=gera_grafo_ja_visitado(hg,w,i,v,k,n_descarte)
				est[(k,v)]=hg[1].root
			elif v in proibidos:
				hg=gera_grafo_proibido(hg,w,v,k,this_context_descarte_counter)
				est[(k,v)]=hg[1].root
			else:
				hg[0].add(((k,v),descarte_counter))
				novo_est={}
				(hg,novo_est,descarte_counter)=constroi_ramo(novo_est,k+1,hg[1],hg[0] ,v,descarte_counter+1)
				est[(k,v)]=novo_est[(k,v)]

		hg=constroi_grafo_disjuntivo(hg,k-1,vw,est)
		imply_intro_conclusion_com_descarte=node_id_hid(str(seqnode)+"=(X"+str(k-1)+vw+" imp q)"+" "+str(this_context_descarte_counter))
		seqnode=seqnode+1
		hg[1].add_node(imply_intro_conclusion_com_descarte)
		hg[1].add_edge(Deduction_Edge(hg[1].root,imply_intro_conclusion_com_descarte))
		hg[1].root=imply_intro_conclusion_com_descarte
		hg=destroi_visitados_ref_nivel(hg,k-1,vw,this_context_descarte_counter)
		est[(k-1,vw)]=hg[1].root
		return (hg,est,descarte_counter)
	else:
#    Verifica se e vw no passo 3 alcanca ini (primeiro) no passo Max+1
		ini=str(0)
		for v in nos:
			for j in range(0,descarte_counter+1):
				if ((1,v),j) in hg[0]:
					ini=v
					label=j

		if not linked(g,vw, ini):
			no_prova_pleft=node_id_hid(str(seqnode)+"=[X"+str(1)+ini+"]"+str(label))
			label_descarte_local=str(descarte_counter)+"a"
			hg[1].add_node(no_prova_pleft)
			seqnode=seqnode+1
			no_prova_pright=node_id_hid(str(seqnode)+"=(X"+str(1)+ini+" imp (X"+str(Max+1)+ini+"))")
			hg[1].add_node(no_prova_pright)
			seqnode=seqnode+1
			no_prova_l=node_id_hid(str(seqnode)+"=X"+str(Max+1)+ini)
			hg[1].add_node(no_prova_l)
			hg[1].add_edge(Deduction_Edge(no_prova_pleft,no_prova_l))
			hg[1].add_edge(Deduction_Edge(no_prova_pright,no_prova_l))
			seqnode=seqnode+1
			no_provaright_pleft=node_id_hid(str(seqnode)+"=[X"+str(Max)+vw+"]"+label_descarte_local)
			seqnode=seqnode+1
			no_provaright_pright=node_id_hid(str(seqnode)+"=(X"+str(Max)+vw+" imp (X"+str(Max+1)+ini+" imp q))")
			seqnode=seqnode+1
			no_provaright=node_id_hid(str(seqnode)+"=(X"+str(Max+1)+ini+" imp q)")
			seqnode=seqnode+1
			no_absurdity=node_id_hid(str(seqnode)+"=q")
			seqnode=seqnode+1
			no_conclusao=node_id_hid(str(seqnode)+"=(X"+str(Max)+vw+" imp q)"+" "+label_descarte_local)
			seqnode=seqnode+1
			hg[1].add_node(no_absurdity)
			hg[1].add_node(no_conclusao)
			hg[1].add_node(no_provaright)
			hg[1].add_node(no_provaright_pleft)
			hg[1].add_node(no_provaright_pright)
			hg[1].add_edge(Deduction_Edge(no_provaright_pleft,no_provaright))
			hg[1].add_edge(Deduction_Edge(no_provaright_pright,no_provaright))
			hg[1].add_edge(Deduction_Edge(no_prova_l,no_absurdity))
			hg[1].add_edge(Deduction_Edge(no_provaright,no_absurdity))
			hg[1].add_edge(Deduction_Edge(no_absurdity,no_conclusao))
			hg[1].root=no_conclusao
			hg=destroi_visitados_ref_nivel(hg,k-1,vw,descarte_counter)
			est[(Max,vw)]=hg[1].root

			return (hg,est,descarte_counter)
		else:
#        print "Achou um ciclo Hamiltoniano"
			return pd.Graph()

def destroi_visitados_ref_nivel(hg,k,vw,n_descarte):
#   print "destruindo tentativas de visita a partir do no="+vw+"no nível="+str(k)
	R=(hg[0]-set([((k,vw),n_descarte)]),hg[1])
	hg=(R,hg[1])

	return R

def constroi_grafo_disjuntivo(hg,nivel,no,lista_provas):
#   print "construindo grafo disjuntivo nivel="+str(nivel)+"no="+no
	global seqnode

	disjunctive_formula="(ORX"+str(nivel+1)+" imp q)"
	labeled_disjunctive_formula_conclusion=node_id_hid(str(seqnode)+"="+disjunctive_formula)
	seqnode=seqnode+1
	hg[1].root=labeled_disjunctive_formula_conclusion
	for ((i1,v1),v) in lista_provas.items():
		hg[1].add_node(labeled_disjunctive_formula_conclusion)
		disjunctive_formula="(X"+str(i1)+v1+" imp q) imp ("+ disjunctive_formula+ ")"
		labeled_disjunctive_formula_premiss=node_id_hid(str(seqnode)+"="+disjunctive_formula)
		seqnode=seqnode+1
		hg[1].add_node(labeled_disjunctive_formula_premiss)
		hg[1].add_edge(Deduction_Edge(labeled_disjunctive_formula_premiss,labeled_disjunctive_formula_conclusion))

		v_prova=v
		hg[1].add_edge(Deduction_Edge(v_prova, labeled_disjunctive_formula_conclusion))
		labeled_disjunctive_formula_conclusion=labeled_disjunctive_formula_premiss

	left_premiss_disjunctive_formula="ORX"+str(nivel+1)
	labeled_left_premiss_disjunctive_formula=node_id_hid(str(seqnode)+"="+left_premiss_disjunctive_formula)
	hg[1].add_node(labeled_left_premiss_disjunctive_formula)
	seqnode=seqnode+1
	absurdity_conclusion="q"
	labeled_absurdity_conclusion=node_id_hid(str(seqnode)+"="+absurdity_conclusion)
	hg[1].add_node(labeled_absurdity_conclusion)
	hg[1].add_edge(Deduction_Edge(labeled_left_premiss_disjunctive_formula,labeled_absurdity_conclusion))
	hg[1].add_edge(Deduction_Edge(hg[1].root,labeled_absurdity_conclusion))
	hg[1].root=labeled_absurdity_conclusion
	seqnode=seqnode+1

	return hg

def linked(g,a,b):
	l=g.get_edge_list()
	res=False
	for e in l:
		if igual(e.get_source(),a) and igual(e.get_destination(),b):
			res=True
	return res

def get_k(v,vis):
	for ((i,w),j) in vis:
		if igual(v,w):
			i1=i
	return i1

def get_descarte(v,vis):
	for ((i,w),j) in vis:
		if igual(v,w):
			j1=j
	return j1

def gera_grafo_ja_visitado(hg,w,i,v,k,label_descarte):
	global seqnode
#   print str(seqnode)+"vai gerar grafo_ja_visitado"+"w= "+w+"i= "+str(i)+"v= "+v+"k="+str(k)
##   print hg[0]
#   hg[0].add((k,v))
	novo_w=node_id_hid(str(seqnode)+"=[X"+str(i)+v+"]"+str(label_descarte))
	hg[1].add_node(novo_w)
	seqnode=seqnode+1
	nova_imp_w=node_id_hid(str(seqnode)+"=(X"+str(i)+vertex_name(v)+" imp "+"(X"+str(k)+v+" imp q))")
	hg[1].add_node(nova_imp_w)
	seqnode=seqnode+1
	w_negado=node_id_hid(str(seqnode)+"=(X"+str(k)+v+" imp q)")
	hg[1].add_node(w_negado)
	hg[1].add_edge(Deduction_Edge(novo_w,w_negado))
	hg[1].add_edge(Deduction_Edge(nova_imp_w,w_negado))
	seqnode=seqnode+1
	hg[1].root=w_negado
	seqnode=seqnode+1
	return hg

def gera_grafo_proibido(hg,w,v,k,label_descarte):
	global seqnode

	novo_w=node_id_hid(str(seqnode)+"=[X"+str(k-1)+w+"]"+str(label_descarte))
	hg[1].add_node(novo_w)

	seqnode=seqnode+1
	nova_imp_w=node_id_hid(str(seqnode)+"=(X"+str(k-1)+vertex_name(w)+" imp "+"(X"+str(k)+v+" imp q))" )
	hg[1].add_node(nova_imp_w)
	seqnode=seqnode+1
	w_negado=node_id_hid(str(seqnode)+"=(X"+str(k)+v+" imp q)")
	hg[1].add_node(w_negado)
	hg[1].add_edge(Deduction_Edge(novo_w,w_negado))
	hg[1].add_edge(Deduction_Edge(nova_imp_w,w_negado))

	hg[1].root=w_negado
	seqnode=seqnode+1
	return hg

def Deduction_Edge(s,d):
	global e_in
	global e_out

	if not e_in.has_key(d.get_name()):
		e_in[d.get_name()]=[]
	if not e_out.has_key(s.get_name()):
		e_out[s.get_name()]=[]
	e=pd.Edge(s,d)
	e_out[s.get_name()].append(e)
	e_in[d.get_name()].append(e)
	return e

def node_id_hid(s):
	return pd.Node(vertex_id(s),label=vertex_label(s))

def igual(c1, c2):
	if not c1 or not c1:
  		return False
	else:
		i=0
		l1=len(c1)
		l2=len(c2)
		while i<=l1-1 and i<=l2-1 and c1[i]==c2[i]:
			i=i+1
		return c1[i-1]==c2[i-1] and i==l1 and i==l2

def vertex_name(w):
	i=0
	while w[i] != "v":
		i=i+1
	return w[i:]

def add_nodes(graph, nodes):
	for n in nodes:
		graph.add_node(n)
	return graph

def add_edges(graph, edges):
	for e in edges:
		graph.add_edge(pd.Edge(e[0],e[1]))
	return graph

def vertex_id(w):
	i=0
	while w[i]!= "=":
		i=i+1
	return w[:i]

def vertex_label(w):
##    print "vertex_labl = "+w
	i=0
	while (w[i]!= "X") and (w[i]!= "O") and (w[i]!= "(") and (w[i]!="q") and (w[i]!="["):
		i=i+1
	return w[i:]

visitados=set()

global seqnode

# discharged_occurrences={}
# conclusions={}

# relativo a eficiencia da versao linked
# associa vertices as arestas incidented que chegam nele
e_in={}
# associa vertices as arestas incidentes que saem dele
e_out={}
# associa vertices as arestas ancestrais (l_A no paper) que saem de cada um deles
e_in_A={}
# associa vertices as arestas ancestrais (l_A no paper) que chegam em  cada um deles
e_out_A={}

seqnode=1

# supondo X[1,v1] como inicio.

visitados.add("v1")

Max=3
nos={"v"+str(i) for i in range(1,Max+1)}
list_nodes=[]
for i in range(1,Max+1):
    list_nodes=list_nodes+[pd.Node("v"+str(i))]

g=pd.Graph()
g=add_nodes(g, list_nodes)
g=add_edges(g,[('v1','v2'),('v1','v3')])

def main():
	proof_graph, a , b, c = inicia()
	sgraph=pd.graph_from_dot_data(proof_graph.to_string())
	sgraph.write("img/"+sgraph.get_name()+"ENTRADA.dot")
	graph_gt = gt.load_graph("img/EntreNiveisVersion3Compressing33G3ENTRADA.dot")
	graph_gt.save("img/test.dot")

if __name__ == '__main__':
	main()
