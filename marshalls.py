from models.HyperGraph import HyperEdge, HyperGraph


def main():

    variables = {'X', 'Y', 'Z', 'W'}
    edge_r = HyperEdge('R', {'X', 'Y'})
    edge_s = HyperEdge('S', {'Y', 'Z'})
    edge_t = HyperEdge('T', {'Z', 'W'})
    edges = {edge_r, edge_s, edge_t}
    graph = HyperGraph(variables, edges)

    print(graph.join_tree(graph.get_vertices(), set()))


if __name__ == "__main__":
    main()