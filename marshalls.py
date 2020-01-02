from models.HyperEdge import HyperEdge
from models.HyperGraph import HyperGraph


def main():
    variables = {'X', 'Y', 'Z', 'W', 'V', 'P', 'U'}
    # edge_r = HyperEdge('R', {'X', 'Y'})
    # edge_s = HyperEdge('S', {'Y', 'Z'})
    # edge_t = HyperEdge('T', {'Z', 'W'})
    # edges = {edge_r, edge_s, edge_t}
    edge_r = HyperEdge('R', {'X', 'Y', 'Z'})
    edge_s = HyperEdge('S', {'X', 'Y', 'U'})
    edge_t = HyperEdge('T', {'Y', 'V', 'W'})
    edge_u = HyperEdge('U', {'Y', 'V', 'P'})
    edges = {edge_r, edge_s, edge_t, edge_u}
    graph = HyperGraph(variables, edges)

    join_tree = graph.join_tree()
    print(join_tree.serialize())
    print(join_tree.generalize().serialize())


if __name__ == "__main__":
    main()