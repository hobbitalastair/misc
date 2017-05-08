""" Colouring algorithm implementations

    Graphs are a collection of edges and vertices.
    The algorithms are supposed to accept a list of vertices and a hash of
    edges, where each edge is composed of two indicies of the list of 
    vertices.
"""

from random import randint

class Vertex:
    def __init__(self, colour=None):
        """ Initialise self """
        self.colour = colour


def naive(vertices, edges):
    """ Find a colouring of the graph by iterating through all possible
        combinations of colours. We start with k = 1, and increase it until
        a colouring is found.
        This algorithm will be extremely slow; each iteration will take
        k^n, where k is the number of colours, and n is the number of vertices.

        >>> v = [Vertex(), Vertex()]
        >>> naive(v, [])
        >>> v[0].colour
        0
        >>> v[1].colour
        0
        >>> naive(v, [(0, 1)])
        >>> v[0].colour != v[1].colour
        True

        >>> v = [Vertex(), Vertex(), Vertex()]
        >>> e = [(0, 1), (1, 2)]
        >>> naive(v, e); is_colouring(v, e)
        True
        >>> e = [(0, 1), (1, 2), (0, 2)]
        >>> naive(v, e); is_colouring(v, e)
        True

        >>> v = [Vertex(), Vertex(), Vertex(), Vertex(), Vertex()]
        >>> e = complete(v); naive(v, e); is_colouring(v, e)
        True
        
        We near the maximum vertex count...
        >>> v = [Vertex(), Vertex(), Vertex(), Vertex(), Vertex(), Vertex()]
        >>> e = complete(v); naive(v, e); is_colouring(v, e)
        True
    """

    k = 1
    while True:
        # Try a colouring using k colours.

        # Bail if this is going to take too long.
        if k**len(vertices) > 100000 or k > len(vertices):
            if k > len(vertices):
                reason = "No colouring exists"
            else:
                reason = "Exceeded maximum check count ({})".format( \
                        k**len(vertices))
            e = "Could not find a colouring in the given graph ({})".format( \
                    reason)
            raise ValueError(e)

        # Iterate through all possible colourings.
        for colouring in range(k**len(vertices)):
            # Recolour.
            for i, v in enumerate(vertices):
                v.colour = colouring % k
                colouring = colouring // k

            if is_colouring(vertices, edges):
                return

        # Increment k.
        k += 1


class TreeVertex(Vertex):
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        self.colouring = []

    def __str__(self):
        return "<TreeVertex {}: {}, {}>".format(id(self), self.colour, \
                self.colouring)

    def __repr__(self):
        return self.__str__()


def tree(vertices, edges):
    """ A less naive approach.
        We create a series of trees, covering all edges, and combine the
        colourings for each of the trees to generate a final colouring.
        I have no idea wether this is correct or not... but it appears to
        work, if not optimally.

        We assume that the graph is simple and connected; it is trivial to
        turn a graph into a simple graph, and colourings of components can
        be combined.
        
        >>> v = [TreeVertex(), TreeVertex()]
        >>> tree(v, [(0, 1)])
        Trees: 1, colours: 2
        >>> v[0].colour != v[1].colour
        True

        >>> v = [TreeVertex(), TreeVertex(), TreeVertex()]
        >>> e = [(0, 1), (1, 2)]
        >>> tree(v, e); is_colouring(v, e)
        Trees: 1, colours: 2
        True

        Complete graphs:
        Note that we expect to have (|v| // 2) + 1 trees, since each tree can
        visit at most |v| - 1 edges, and there are (|v| * (|v| - 1)) / 2 edges
        in total, or roughly |v|^2 / 2 edges.
        >>> v = [TreeVertex() for i in range(3)]
        >>> e = complete(v); tree(v, e); is_colouring(v, e)
        Trees: 2, colours: 3
        True
        
        >>> v = [TreeVertex() for i in range(5)]
        >>> e = complete(v); tree(v, e); is_colouring(v, e)
        Trees: 3, colours: 5
        True

        >>> v = [TreeVertex() for i in range(20)]
        >>> e = complete(v); tree(v, e); is_colouring(v, e)
        Trees: 11, colours: 20
        True

        >>> v = [TreeVertex() for i in range(50)]
        >>> e = complete(v); tree(v, e); is_colouring(v, e)
        Trees: 26, colours: 50
        True

        Cycles:
        Note that we need *4* colours here, due to the limitations of the
        algorithm.
        >>> v = [TreeVertex() for i in range(7)]
        >>> e = [(i, (i + 1) % 7) for i in range(7)]
        >>> tree(v, e); is_colouring(v, e)
        Trees: 2, colours: 4
        True

        >>> v = [TreeVertex() for i in range(20)]
        >>> e = [(i, (i + 1) % 20) for i in range(20)]
        >>> tree(v, e); is_colouring(v, e)
        Trees: 2, colours: 2
        True

        >>> v = [TreeVertex() for i in range(40)]
        >>> e = [(i, (i + 1) % 40) for i in range(40)]
        >>> tree(v, e); is_colouring(v, e)
        Trees: 2, colours: 2
        True

        Wheels:
        >>> w = 6
        >>> v = [TreeVertex() for i in range(w)]
        >>> e = [(i, (i + 1) % (w - 1)) for i in range(w - 1)] + \
                [((w - 1), i) for i in range((w - 1))]
        >>> tree(v, e); is_colouring(v, e)
        Trees: 2, colours: 4
        True

        >>> w = 7
        >>> v = [TreeVertex() for i in range(w)]
        >>> e = [(i, (i + 1) % (w - 1)) for i in range(w - 1)] + \
                [((w - 1), i) for i in range((w - 1))]
        >>> tree(v, e); is_colouring(v, e)
        Trees: 2, colours: 3
        True
    """

    # Keep track of all visited and unvisited edges.
    unvisited = set(edges)
    visited = []

    # Cache the degree of each vertex
    degrees = {i: 0 for i, _ in enumerate(vertices)}
    for e in edges:
        degrees[e[0]] += 1
        degrees[e[1]] += 1


    while len(unvisited) > 0:
        # Create a tree.

        # We start by finding unvisited edges and adding them. Once we
        # have exhausted the possible unvisited edges which would not create
        # a cycle, we finish the tree by adding visited edges.

        # Keep track of the tree.
        tree_size = 0
        v_edges = [[] for i in range(len(vertices))]
        # Also record the components.
        components = {}

        def try_edge(e):
            """ Helper function; try the edge and add it if it does not
                create a cycle.
            """

            # Check that the edges are not already in one component.
            c1 = None
            c2 = None
            for i, c in components.items():
                if e[0] in c:
                    c1 = i
                if e[1] in c:
                    c2 = i
                if c1 is not None and c2 is not None:
                    # Break early.
                    if c1 == c2:
                        return 0
                    break
            
            # Add the edge.
            v_edges[e[0]].append(e[1])
            v_edges[e[1]].append(e[0])

            if c1 is None and c2 is None:
                # Both c1 and c2 are None; create a new component containing
                # both vertices.
                components[e[0]] = set(e)
            elif c1 is not None and c2 is not None:
                # Both are in different components; merge the components.
                components[c1] = components[c1].union(components[c2])
                del(components[c2])
            elif c1 is not None:
                # e[0] is in a component, e[1] isn't.
                components[c1].add(e[1])
            else:
                # e[1] is in a component, e[0] isn't.
                components[c2].add(e[0])
            return 1

        # The algorithm here needs to be careful when picking trees - a
        # simple pathological case is for wheels, where random trees often
        # end up needing three trees instead of two.
        #
        # A good rule-of-thumb seems to be to pick the edge with the minimum
        # degree of the first vertex, then of the second vertex, then the
        # vertex with a minimum number of total adjacent edges from earlier
        # trees, then by the second vertex having the minimum number of total
        # adjacent edges.
        #
        # The implementation here just relies on picking using a minimal
        # degree.
        # TODO: A priority queue or similar should be able to provide a
        #       speedup here.
        remaining = unvisited.copy()
        while len(remaining) > 0:
            e = min(remaining, key=lambda e: min(degrees[e[0]], degrees[e[1]]))
            remaining.remove(e)
            tree_size += try_edge(e)

        v_p = 0 # Visited edge position marker.
        while tree_size < (len(vertices) - 1):
            # Add a vertex to the tree from the 'visited' vertices.
            if v_p >= len(visited):
                raise ValueError("The given graph has more than one component!")
            tree_size += try_edge(visited[v_p])
            v_p += 1
        
        # Update the visited/unvisited lists.
        for v, adj in enumerate(v_edges):
            for u in adj:
                for order in ((v, u), (u, v)):
                    if order in unvisited:
                        unvisited.remove(order)
                        visited.append(order)

        # Walk the tree, and update the colouring markers.
        visited_children = {0}
        children = [0]
        colour = 0
        vertices[0].colouring.append(0)
        while len(children) > 0:
            parents = children
            children = []
            colour = (colour + 1) % 2 # 0 or 1
            for parent in parents:
                # Find the children of the parent, add them, and colour them.
                for child in v_edges[parent]:
                    if child not in visited_children:
                        visited_children.add(child)
                        vertices[child].colouring.append(colour)
                        children.append(child)

    # Colour the graph.
    #
    # Note that the result can be expressed as a much simplified graph, where
    # there are 2^k vertices, where k is the number of trees, and there is an
    # edge for each pair of vertices which cannot be the same colour.
    # The solution is then a colouring of that graph (!)
    #
    # The current method could be made more optimal, eg if the requirement for
    # a tree was relaxed to just a forest.
    colours = set()
    for v in vertices:
        v.colour = sum([b << i for i, b in enumerate(v.colouring)])
        colours.add(v.colour)
    # Print the number of trees and colours required.
    print("Trees: {}, colours: {}".format(len(v.colouring), len(colours)))


def is_colouring(vertices, edges):
    """ Check if the given graph is a colouring.
    
        >>> is_colouring([Vertex("c1"), Vertex("c2")], [(0, 1)])
        True
        >>> is_colouring([Vertex("c1")], [(0, 0)])
        False
        >>> is_colouring([Vertex("c1"), Vertex("c1")], [(0, 1)])
        False
        >>> is_colouring([Vertex("c1"), Vertex("c2"), Vertex("c1")], \
                [(0, 1), (1, 2)])
        True
        >>> is_colouring([Vertex("c1"), Vertex("c2"), Vertex("c1")], \
                [(0, 1), (1, 2), (0, 2)])
        False
    """

    # Iterate through all the edges; if the two vertices have the same
    # colour, fail.
    for edge in edges:
        if vertices[edge[0]].colour == vertices[edge[1]].colour:
            return False
    return True


def complete(vertices):
    """ Generate a complete set of edges for the given vertices
    
        >>> complete([Vertex()])
        []
        >>> sorted(complete([Vertex(), Vertex(), Vertex()]))
        [(0, 1), (0, 2), (1, 2)]
    """

    return [(i, v) for i in range(len(vertices)) \
            for v in range(i+1, len(vertices))]


def random_connected(vertices):
    """ Generate a random connected graph

        >>> v = [Vertex() for i in range(5)]; e = random_connected(v); \
                connected(v, e)
        True
        >>> v = [Vertex() for i in range(10)]; e = random_connected(v); \
                connected(v, e)
        True
        >>> v = [Vertex() for i in range(100)]; e = random_connected(v); \
                connected(v, e)
        True
    """

    # Initialise the edge set.
    e = set()

    # Initialise the remaining edge set.
    remaining = complete(vertices)

    components = {}
    visited = set()
    while not (len(visited) == len(vertices) and len(components) == 1) \
            and len(remaining) != 0:
        # Keep on adding edges until the graph is connected.
        index = randint(0, len(remaining) - 1)
        v0, v1 = remaining.pop(index)
        e.add((v0, v1))
        visited.add(v0)
        visited.add(v1)
        # Find the vertices in the components.
        c0 = None
        c1 = None
        for i, c in components.items():
            if v0 in c:
                c0 = i
            if v1 in c:
                c1 = i
        # Merge/add them to the components as required.
        if c0 == None:
            if c1 == None:
                # Both are not added; create a new component.
                components[v0] = {v0, v1}
            else:
                # Add v0 to v1's component.
                components[c1].add(v0)
        else:
            if c1 == None:
                # Add v1 to v0's component.
                components[c0].add(v1)
            else:
                # Merge the components.
                components[c0] = components[c0].union(components[c1])
                del(components[c1])
            
    return e
    

def random(vertices):
    """ Generate a random set of edges for the given vertices
    
        >>> e = random([Vertex()] * 5)
        >>> e = random([Vertex()] * 10)
    """

    # Initialise the edge set.
    e = complete(vertices)

    # Pick some number of edges to remove.
    d = randint(0, len(e) - 1)
    while d > 0:
        e.pop(randint(0, len(e) - 1))
        d -= 1

    return e


def connected(vertices, edges):
    """ Return True if the given graph is connected.

        >>> v = [0] * 5
        >>> connected(v, complete(v))
        True
        >>> connected(v, [])
        False
        >>> connected(v, [(0, 1), (1, 2), (2, 3), (3, 4)])
        True
        >>> connected(v, [(0, 1), (1, 4), (2, 3), (3, 4)])
        True
        >>> connected(v, [(0, 1), (1, 2), (2, 0), (3, 4)])
        False
    """

    visited = set()

    stack = [0]
    while len(stack) != 0:
        v = stack.pop()
        visited.add(v)
        for edge in edges:
            if edge[0] == v and edge[1] not in visited:
                stack.append(edge[1])
            elif edge[1] == v and edge[0] not in visited:
                stack.append(edge[0])

    return len(visited) == len(vertices)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
