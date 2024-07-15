
# Trie struktura podataka
class TrieNode:
    __slots__ = '_char', '_children', '_end_of_word', '_frequency', '_index'

    def __init__(self, char=''):
        self._char = char
        self._children = {}
        self._end_of_word = False
        self._frequency = 0
        self._index = []

    @property
    def char(self):
        return self._char

    @char.setter
    def char(self, value):
        self._char = value

    @property
    def children(self):
        return self._children

    @children.setter
    def children(self, value):
        self._children = value

    @property
    def end_of_word(self):
        return self._end_of_word

    @end_of_word.setter
    def end_of_word(self, value):
        self._end_of_word = value

    @property
    def frequency(self):
        return self._frequency

    @frequency.setter
    def frequency(self, value):
        self._frequency = value

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, value):
        self._index = value


# Funkcija koja dodaje rec u Trie stablo
def add_word(root, word, index):
    node = root

    # Dodajemo svaki karakter reci u Trie stablo
    for char in word:
        if char not in node.children:
            node.children[char] = TrieNode(char)
        node = node.children[char]

    # Oznacavamo kraj reci
    node.end_of_word = True
    node.frequency += 1

    # Dodajemo indeks stranice u listu indeksa
    if index not in node.index:
        node.index.append(index)
