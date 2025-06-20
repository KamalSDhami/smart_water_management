import networkx as nx

def compute_mst(G):
    # Returns MST as a networkx.Graph
    mst = nx.minimum_spanning_tree(G, weight='weight', algorithm='prim')
    return mst