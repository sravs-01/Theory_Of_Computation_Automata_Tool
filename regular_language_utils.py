from graphviz import Digraph

eps = '&#949;'  # HTML entity for epsilon

def subgraphForSymbol(dot, symbol, node_count):
    start_node = f'q{node_count}'
    end_node = f'q{node_count + 1}'
    node_count += 2

    dot.node(start_node)
    dot.node(end_node, shape='doublecircle')

    dot.edge(start_node, end_node, label=symbol)

    return start_node, end_node

def subgraphForUnion(parentGraph: Digraph, nodes0, nodes1, node_count: int):
    newLabel1 = f'q{node_count}'
    newLabel2 = f'q{node_count + 1}'

    parentGraph.node(newLabel1, label=f'<q<sub>{node_count}</sub>>')
    parentGraph.node(newLabel2, label=f'<q<sub>{node_count + 1}</sub>>')

    parentGraph.edge(newLabel1, nodes0[0], label=eps)
    parentGraph.edge(newLabel1, nodes1[0], label=eps)

    parentGraph.edge(nodes0[1], newLabel2, label=eps)
    parentGraph.edge(nodes1[1], newLabel2, label=eps)

    return [newLabel1, newLabel2]

def subgraphForConcatenation(parentGraph: Digraph, nodes0, nodes1):
    parentGraph.edge(nodes0[1], nodes1[0], label=eps)

    return [nodes0[0], nodes1[1]]

def subgraphForClosure(parentGraph: Digraph, nodes, node_count: int):
    newLabel = f'q{node_count}'

    parentGraph.node(newLabel, label=f'<q<sub>{node_count}</sub>>')

    parentGraph.edge(newLabel, nodes[0], label=eps)
    parentGraph.edge(nodes[1], nodes[0], label=eps, constraint='false')
    parentGraph.edge(newLabel, nodes[1], label=eps, constraint='false')

    return [newLabel, nodes[1]]