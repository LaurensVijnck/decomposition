from models.HyperEdge import HyperEdge
from models.HyperGraph import HyperGraph
from models.Relation import MultisetRelation


def main():
    variables = {'X', 'Y', 'Z', 'W', 'V', 'U'}
    edge_r = HyperEdge('R', {'X', 'Y', 'Z'})
    edge_s = HyperEdge('S', {'X', 'Y', 'U'})
    edge_t = HyperEdge('T', {'Y', 'V', 'W'})
    edges = {edge_r, edge_s, edge_t}
    graph = HyperGraph(variables, edges)

    join_tree = graph.join_tree()
    print(join_tree.serialize())
    print(join_tree.generalize().serialize())
    
    r = MultisetRelation.from_file("R", "data/relations/R.txt")
    s = MultisetRelation.from_file("S", "data/relations/S.txt")
    t = MultisetRelation.from_file("T", "data/relations/T.txt")

if __name__ == "__main__":
    main()
