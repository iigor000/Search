import re
import parse_txt_files
from graph import Graph
from trie import TrieNode, add_word
import os
import pickle
from spellchecker import SpellChecker
from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER


# Funkcija koja kreira graf stranica
def build_graph(directory):
    # Regularni izraz koji prepoznaje reference na stranice
    # ( see page 5, on page 5, see pages 5 and 6, on pages 5 and 6)
    ref_pattern = re.compile(r'(?:see|on) pages? (\d+(?:\s*and\s*\d+)*)', re.IGNORECASE)
    referenced_pages = {}

    # Učitavanje rezultata iz tekstualnih fajlova
    results = parse_txt_files.read_results_from_files(directory)

    # Kreiranje praznog usmerenog grafa
    graph = Graph(True)

    for key in results:
        page = results[key]

        # Čišćenje teksta od specijalnih karaktera
        content = clean_text(page['content'])
        words = content.split()

        # Kreiranje Trie strukture za svaku stranicu
        root = TrieNode()
        for i, word in enumerate(words):
            add_word(root, word.lower(), i)
        matches = ref_pattern.findall(content)

        # Dodavanje stranica na koje se referiše u graf
        references = [page.strip() for match in matches for page in match.split(' and ')]
        for reference in references:
            if reference not in referenced_pages:
                referenced_pages[reference] = [page['page_number']]
            else:
                referenced_pages[reference].append(page['page_number'])
        graph.insert_vertex(root, page['page_number'], key)

    # Dodavanje grana između stranica koje se referišu
    for ref in referenced_pages:
        for page in referenced_pages[ref]:
            u = graph.get_vertex_by_number(page)
            v = graph.get_vertex_by_number(int(ref))
            if u is not None and v is not None:
                graph.insert_edge(u, v)

    return graph


# Funkcija koja čisti tekst od specijalnih karaktera
def clean_text(text):
    return (text.replace('\n', ' ').replace(',', '').replace('.', '').replace('(', '')
                .replace(')', '').replace("’", ' ').replace('"', '').replace(":", '')
                .replace(";", '').replace("?", '').replace("!", '').replace('”', '')
                .replace('“', '').replace('—', '').replace('–', '').replace('‘', '')
                .replace('’', '').replace('…', '').replace('•', '').replace('\t', ''))


# Funkcija koja pronalazi prvo pojavljivanje reči u tekstu (za prikaz u konzoli)
def find_snippet(words_to_highlight, page, root):
    # Učitavanje teksta iz tekstualnog fajla
    file = os.path.join(root, f'{page}.txt')
    text = parse_txt_files.read_results_from_file(file).decode('utf-8').replace('\n', ' ')
    # Čišćenje teksta od specijalnih karaktera (visestruki razmaci i tabovi)
    text = re.sub('[ \t]+', ' ', text)
    words = text.split()

    # Pronalaženje okolnih reči za svaku reč koja se traži
    for word_to_highlight in words_to_highlight:
        # Pretraga reči u tekstu
        match = re.search(r'\b' + re.escape(word_to_highlight.lower()) + r'\b', text.lower())
        if match:
            # Pronalaženje okolnih reči
            start = len(text[:match.start()].split()) - 1
            end = start + len(word_to_highlight.split())
            surrounding_words = words[max(0, start - 3):min(len(words), end + 3)]
            surrounding_text = ' '.join(surrounding_words)

            # Označavanje reči koje se traže
            surrounding_text = highlight_words(surrounding_text, words_to_highlight)
            return surrounding_text
    return ''


# Funkcija koja označava reči u tekstu
def highlight_words(text, words_to_highlight):
    # Početak i kraj oznake za bojenje teksta
    start = '\033[30;43m'
    end = '\033[0m'
    for word in words_to_highlight:
        escaped_word = re.escape(word)
        # Bojenje reči u tekstu
        text = re.sub(f'\\b{escaped_word}\\b', f'{start}\\g<0>{end}', text, flags=re.IGNORECASE)
    return text


# Funkcija koja čuva graf u fajlu
def save_graph(graph, name):
    path = os.path.join('..', 'graphs', name + '.pkl')
    with open(path, 'wb') as f:
        pickle.dump(graph, f)


# Funkcija koja vrši pretragu po upitu
def page_rank(postfix, graph):
    stack = []
    # Tokenizacija upita (fraze ostaju u celini)
    tokens = re.findall(r'"[^"]*"|\S+', postfix)

    for token in tokens:
        if token in ['AND', 'OR', 'NOT']:
            # Za AND operator, izvršava se presek stranica
            if token == 'AND':
                operand2 = stack.pop()
                operand1 = stack.pop()
                result = [vertex for vertex in operand1 if vertex in operand2]
                stack.append(result)
            # Za OR operator, izvršava se unija stranica
            elif token == 'OR':
                operand2 = stack.pop()
                operand1 = stack.pop()
                result = list(set(operand1 + operand2))
                stack.append(result)
            # Za NOT operator, izvršava se razlika stranica
            elif token == 'NOT':
                operand1 = stack.pop()
                operand2 = stack.pop()
                result = [vertex for vertex in operand2 if vertex not in operand1]
                stack.append(result)
        else:
            if '"' in token:  # Provera da li je token fraza
                phrase = token.replace('"', '')  # Uklanjanje navodnika iz fraze
                vertices = find_phrase(phrase, graph)  # Pronalaženje stranica koje sadrže frazu
                stack.append(vertices)
            else:
                token = token.lower()
                vertices = []
                # Pronalaženje stranica koje sadrže reč
                for vertex in graph.vertices():
                    node = vertex.trie()
                    for char in token:
                        if char in node.children:
                            node = node.children[char]
                        else:
                            node = None
                            break
                    if node is not None and node.end_of_word:
                        vertex.add_score(node.frequency)
                        vertices.append(vertex)
                stack.append(vertices)

    # Računanje vrednosti stranica na osnovu referenca
    for vertex in stack[0]:
        for edge in graph.incident_edges(vertex, False):
            if not vertex.score() == 0:
                vertex.add_score(edge.opposite(vertex).score() * 2)

    # Sortiranje stranica po vrednosti
    sorted_pages = sorted([vertex for vertex in stack[0]], key=lambda x: x.score(), reverse=True)

    return sorted_pages


# Klasa koja predstavlja reč u frazi
class Word:
    def __init__(self, word, indexes):
        self.word = word
        self.indexes = indexes


def find_phrase(phrase, graph):
    phrase = phrase.split()
    pages = {}

    # Pronalaženje stranica koje sadrže frazu
    for word in phrase:
        for vertex in graph.vertices():
            node = vertex.trie()
            for char in word:
                if char in node.children:
                    node = node.children[char]
                else:
                    node = None
                    break
            if node is not None and node.end_of_word:
                # Dodavanje stranice u rečnik
                pages.setdefault(vertex.index(), []).append(Word(word, node.index))

    # Pronalaženje stranica koje sadrže celu frazu
    for page, words in pages.items():
        counter = 0
        for i in words[0].indexes:
            # Provera da li se reči nalaze na istim pozicijama
            for j in range(1, len(phrase)):
                if len(phrase) != len(words):
                    break
                if phrase[j] == words[j].word and i + j in words[j].indexes:
                    if j == len(words) - 1:
                        counter += 1
                else:
                    break
        # Dodavanje broja pojavljivanja fraze na stranici
        graph.get_vertex_by_index(page).add_score(counter)

    return [vertex for vertex in graph.vertices() if vertex.score() > 0]


# Funkcija koja transformiše infix izraz u postfix
def transform_query(infix, graph):
    # Operatori i njihova prioritet
    precedence = {'NOT': 1, 'AND': 1, 'OR': 1, '(': 0, ')': 0}
    output = []
    stack = []
    parentheses_counter = 0
    last_token = None
    words = []

    # Provera da li je fraza dobro napisana
    if infix.count('"') % 2 != 0:
        raise ValueError('Fraza nije dobro napisana.')

    # Tokenizacija upita
    tokens = re.findall(r'"[^"]*"|\b\w+\b|\(|\)', infix)

    # Provera da li postoji zvezdica u reči
    for i, token in enumerate(tokens):
        if '*' in token:
            # Pronalaženje reči sa istim prefiksom
            word = select_word_endings(find_common_prefix_words(token[:-1], graph))
            tokens[i] = word

    for token in tokens:
        # Provera da li je token operator
        if token not in precedence:
            # Provera da li je potrebno dodati OR operator
            if last_token and last_token not in precedence:
                while stack and precedence[stack[-1]] >= precedence['OR']:
                    output.append(stack.pop())
                stack.append('OR')
            # Dodavanje fraza u listu reči
            if token.startswith('"') and token.endswith('"'):
                words.append(token[1:-1])
            else:
                words.append(token)
            output.append(token)
        elif token == '(':
            parentheses_counter += 1
            stack.append(token)
        elif token == ')':
            parentheses_counter -= 1
            if parentheses_counter < 0:
                raise ValueError("Unmatched right parenthesis.")
            top_token = stack.pop()
            while top_token != '(':
                output.append(top_token)
                top_token = stack.pop()
        else:
            while stack and precedence[stack[-1]] >= precedence[token]:
                output.append(stack.pop())
            stack.append(token)
        last_token = token

    if parentheses_counter != 0:
        raise ValueError("Unmatched left parenthesis.")

    while stack:
        output.append(stack.pop())

    # Vraćanje postfix izraza i reči
    return ' '.join(output), words


# Funkcija u kojoj korisnik bira nastavak reči
def select_word_endings(words):
    for i in range(len(words)):
        print(f'{i + 1}. {words[i]}')
    while True:
        try:
            choice = int(input('Izaberite zeljeni nastavak: '))
            if 1 <= choice <= len(words):
                return words[choice - 1]
        except ValueError:
            pass
        print('Neispravan unos, pokusajte ponovo.')


# Funckija koja trazi reci sa zadatim prefiksom
def find_words_with_prefix(node, prefix):
    for char in prefix:
        if char in node.children:
            node = node.children[char]
        else:
            return []
    return find_all_words(node, prefix)


# Funkcija koja pronalazi sve reči u Trie strukturi sa prefiksom (rekurzivna)
def find_all_words(node, prefix='', words=None):
    if words is None:
        words = []
    if node.end_of_word:
        words.append(prefix)
    for char, child in node.children.items():
        find_all_words(child, prefix + char, words)
    return words


# Funkcija koja pronalazi reči sa zajedničkim prefiksom
def find_common_prefix_words(prefix, graph):
    word_counts = {}

    for vertex in graph.vertices():
        words = find_words_with_prefix(vertex.trie(), prefix)
        for word in words:
            if word in word_counts:
                word_counts[word] += 1
            else:
                word_counts[word] = 1

    # Sortiranje reči po broju pojavljivanja
    sorted_word_counts = sorted(word_counts.items(), key=lambda item: item[1], reverse=True)

    # Vraćanje reči sa zajedničkim prefiksom (prvih 5)
    top_5_words = [word for word, count in sorted_word_counts[:5]]

    return top_5_words


# Funkcija koja proverava da li je upit dobro napisan
def did_you_mean(query):
    spell = SpellChecker()
    query = query.split()
    for i in range(len(query)):
        misspelled = spell.unknown([query[i]])
        if misspelled:
            query[i] = spell.correction(query[i])
    return ' '.join(query)


# Funkcija koja kreira PDF dokument sa rezultatima pretrage
def create_pdf(results, words_to_highlight, filename, file):
    filename = filename.replace('"', "'")
    filename = os.path.abspath(filename + '.pdf')

    doc = SimpleDocTemplate(filename)

    styles = getSampleStyleSheet()

    # Postavljanje stilova za naslov i tekst
    styles['Heading1'].alignment = TA_CENTER
    styles['Heading1'].fontSize = 20
    styles['Heading1'].spaceAfter = 20
    styles['BodyText'].fontSize = 11
    styles['BodyText'].leading = 10

    flowables = []

    for i, result in enumerate(results[:10]):
        # Učitavanje teksta iz tekstualnog fajla
        with open(os.path.join('..', 'txts', file, f'{result.index()}.txt'), 'r', encoding='utf-8') as f:
            content = f.readlines()
            # Označavanje reči u tekstu (žutom bojom)
            for word in words_to_highlight:
                content = [re.sub(f'\\b{word}\\b', f'<span backcolor="yellow">\\g<0></span>', line, flags=re.IGNORECASE)
                           for line in content]
            flowables.append(Paragraph(f'Page {result.index()}\n', styles['Heading1']))
            # Dodavanje teksta u PDF dokument
            for line in content:
                flowables.append(Paragraph(line, styles['BodyText']))
            flowables.append(PageBreak())

    # Čuvanje PDF dokumenta
    doc.build(flowables)
