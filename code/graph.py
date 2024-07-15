class Graph:

    """ Reprezentacija jednostavnog grafa"""

    # ------------------------- Ugnježdena klasa Vertex -------------------------
    class Vertex:
        """ Struktura koja predstavlja čvor grafa."""
        __slots__ = '_trie', '_number', '_index', '_score'

        def __init__(self, trie, number, index, score=0):
            self._trie = trie
            self._number = number
            self._index = index
            self._score = score

        def trie(self):
            return self._trie

        def number(self):
            return self._number

        def index(self):
            return self._index

        def score(self):
            return self._score

        def set_score(self, score):
            self._score = score

        def add_score(self, score):
            self._score += score

        def __hash__(self):         # omogućava da Vertex bude ključ mape
            return hash(id(self))

        def __str__(self):
            return str(self._index)

    # ------------------------- Ugnježdena klasa Edge -------------------------
    class Edge:
        """ Struktura koja predstavlja ivicu grafa """
        __slots__ = '_origin', '_destination', '_element'

        def __init__(self, origin, destination, element):
            self._origin = origin
            self._destination = destination
            self._element = element

        def endpoints(self):
            """ Vraća torku (u,v) za čvorove u i v."""
            return self._origin, self._destination

        def opposite(self, v):
            """ Vraća čvor koji se nalazi sa druge strane čvora v ove ivice."""
            if not isinstance(v, Graph.Vertex):
                raise TypeError('v mora biti instanca klase Vertex')
            if self._destination == v:
                return self._origin
            elif self._origin == v:
                return self._destination
            raise ValueError('v nije čvor ivice')

        def element(self):
            """ Vraća element vezan za ivicu"""
            return self._element

        def __hash__(self):         # omogućava da Edge bude ključ mape
            return hash((self._origin, self._destination))

        def __str__(self):
            return '({0},{1},{2})'.format(self._origin, self._destination, self._element)

        def increment_element(self):
            self._element += 1

    # ------------------------- Metode klase Graph -------------------------
    def __init__(self, directed=False):
        """ Kreira prazan graf (podrazumevana vrednost je da je neusmeren).

        Ukoliko se opcioni parametar directed postavi na True, kreira se usmereni graf.
        """
        self._outgoing = {}
        # ukoliko je graf usmeren, kreira se pomoćna mapa
        self._incoming = {} if directed else self._outgoing

    def _validate_vertex(self, v):
        """ Proverava da li je v čvor(Vertex) ovog grafa."""
        if not isinstance(v, self.Vertex):
            raise TypeError('Očekivan je objekat klase Vertex')
        if v not in self._outgoing:
            raise ValueError('Vertex ne pripada ovom grafu.')

    def is_directed(self):
        """ Vraća True ako je graf usmeren; False ako je neusmeren."""
        return self._incoming is not self._outgoing  # graf je usmeren ako se mape razlikuju

    def vertex_count(self):
        """ Vraća broj čvorova u grafu."""
        return len(self._outgoing)

    def vertices(self):
        """ Vraća iterator nad svim čvorovima grafa."""
        return self._outgoing.keys()

    def edge_count(self):
        """ Vraća broj ivica u grafu."""
        total = sum(len(self._outgoing[v]) for v in self._outgoing)
        # ukoliko je graf neusmeren, vodimo računa da ne brojimo čvorove više puta
        return total if self.is_directed() else total // 2

    def edges(self):
        """ Vraća set svih ivica u grafu."""
        result = set()       # pomoću seta osiguravamo da čvorove neusmerenog grafa brojimo samo jednom
        for secondary_map in self._outgoing.values():
            result.update(secondary_map.values())    # dodavanje ivice u rezultujući set
        return result

    def get_edge(self, u, v):
        """ Vraća ivicu između čvorova u i v ili None ako nisu susedni."""
        self._validate_vertex(u)
        self._validate_vertex(v)
        return self._outgoing[u].get(v)

    # dodata metoda za dohvatanje čvora po broju
    def get_vertex_by_number(self, x):
        for vertex in self.vertices():
            if vertex.number() == x:
                return vertex
        return None

    # dodata metoda za dohvatanje čvora po indeksu
    def get_vertex_by_index(self, x):
        for vertex in self.vertices():
            if vertex.index() == x:
                return vertex
        return None

    def degree(self, v, outgoing=True):
        """ Vraća stepen čvora - broj(odlaznih) ivica iz čvora v u grafu.

        Ako je graf usmeren, opcioni parametar outgoing se koristi za brojanje dolaznih ivica.
        """
        self._validate_vertex(v)
        adj = self._outgoing if outgoing else self._incoming
        return len(adj[v])

    def incident_edges(self, v, outgoing=True):
        """ Vraća sve (odlazne) ivice iz čvora v u grafu.

        Ako je graf usmeren, opcioni parametar outgoing se koristi za brojanje dolaznih ivica.
        """
        self._validate_vertex(v)
        adj = self._outgoing if outgoing else self._incoming
        for edge in adj[v].values():
            yield edge

    def insert_vertex(self, trie, number, index, score=0):
        """ Ubacuje i vraća novi čvor (Vertex) sa elementom x"""
        v = self.Vertex(trie, number, index, score)
        self._outgoing[v] = {}
        if self.is_directed():
            self._incoming[v] = {}        # mapa različitih vrednosti za dolazne čvorove
        return v

    def insert_edge(self, u, v):
        """ Ubacuje i vraća novu ivicu (Edge) od u do v sa pomoćnim elementom x.

        Baca ValueError ako u i v nisu čvorovi grafa.
        Baca ValueError ako su u i v već povezani.
        """

        if self.get_edge(u, v) is not None:      # uključuje i proveru greške
            self.get_edge(u, v).increment_element()

        e = self.Edge(u, v, 1)
        self._outgoing[u][v] = e
        self._incoming[v][u] = e
