from models.HyperEdge import HyperEdge
from models.HyperGraph import HyperGraph
from models.Relation import MultisetRelation, RelationalCatalog


def main():
    variables = {'X', 'Y', 'Z', 'W', 'V', 'U'}
    edge_r = HyperEdge('R', {'X', 'Y', 'Z'})
    edge_s = HyperEdge('S', {'X', 'Y', 'U'})
    edge_t = HyperEdge('T', {'Y', 'V', 'W'})
    edges = {edge_r, edge_s, edge_t}
    graph = HyperGraph(variables, edges)

    join_tree = graph.join_tree()
    gjt = join_tree.generalize()

    catalog = RelationalCatalog()
    catalog.add(MultisetRelation.from_file("R", "data/relations/R.txt"))
    catalog.add(MultisetRelation.from_file("S", "data/relations/S.txt"))
    catalog.add(MultisetRelation.from_file("T", "data/relations/T.txt"))

    print(catalog.get("R").project({'X'}).print())

    gjt.initialize(catalog)

    print(gjt.serialize())




if __name__ == "__main__":
    main()
