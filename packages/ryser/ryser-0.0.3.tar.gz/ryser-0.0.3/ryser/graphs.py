import networkx

def latin_graph(size):
    """The cartesian product of the complete graph with 'size' vertices with
    itself."""
    K = networkx.complete_graph(size)
    return networkx.cartesian_product(K, K)

def symmetric_latin_graph(size):
    """The graph described on p.20 of 
      "Completing Partial Latin Squares: Cropper's Question"
           by Bobga, Goldwasser, Hilton and Johnson. """
    G = latin_graph(size)
    def V(n):
        return [(i,j) for i in range(n) for j in range(n) if i <= j]
    G2 = G.subgraph(V(size))
    def suitable(v, w): 
        return v[0]<v[1] and v[1]==w[0] and w[0]<w[1]
    for v in G2.nodes():
        for w in G2.nodes():
            if suitable(v,w):
                G2.add_edge(v,w)
    return G2
