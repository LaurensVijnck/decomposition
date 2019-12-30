from models.HyperGraph import HyperGraph


def main():
    variables = {'X', 'Y', 'Z', 'W'}
    edges = {frozenset({'X', 'Y'}), frozenset({'Y', 'Z'}), frozenset({'Z', 'W'})}
    graph = HyperGraph(variables, edges)

    print(graph.join_tree(graph.get_vertices(), {}))


if __name__ == "__main__":
    main()