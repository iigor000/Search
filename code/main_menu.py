from search import build_graph, page_rank, find_snippet, save_graph, transform_query, did_you_mean, create_pdf
import os
import pickle
from parse_txt_files import pdf_to_text_files


if __name__ == '__main__':
    # Petlja koja trazi fajl sve dok korisnik ne unese ispravnu putanju
    while True:
        pdf = input('Unesite ime fajla koji zelite da pretrazite: ')

        # Pravimo putanje do pdf fajla, txt foldera i foldera za graf
        pdf_file = os.path.join('..', 'pdf', pdf + '.pdf')
        pdf_dir = os.path.join('..', 'txts', pdf)
        graph_file = os.path.join('..', 'graphs', pdf + '.pkl')

        # Proveravamo da li postoji graf, folder sa tekstualnim fajlovima ili pdf fajl
        # Ako postoji graf, ucitavamo ga
        if os.path.isfile(graph_file):
            with open(graph_file, 'rb') as f:
                graph = pickle.load(f)
                break
        # Ako postoji folder sa tekstualnim fajlovima, pravimo graf
        elif os.path.isdir(pdf_dir):
            graph = build_graph(pdf_dir)
            save_graph(graph, pdf)
            break
        # Ako postoji pdf fajl, pravimo tekstualne fajlove i graf
        elif os.path.isfile(pdf_file):
            pdf_to_text_files(pdf_file)
            graph = build_graph(pdf_dir)
            save_graph(graph, pdf)
            break

        print('Neispravna putanja, pokusajte ponovo.')

    # Petlja koja trazi unos korisnika sve dok korisnik ne unese kraj
    query = input('Unesite pretragu: ')

    # Pretvaramo upit u listu reci (za kasniji prikaz) i transformisemo ga
    transformed_query, words = transform_query(query, graph)

    # Vrsimo pretragu i dobijamo stranice koje su najrelevantnije
    pages = page_rank(transformed_query, graph)

    counter = 1
    for page in pages:
        # Prikazujemo indeks stranice i isecak teksta
        print(f'{counter}. Index stranice: {page.index()}')
        print(find_snippet(words, page.index(), pdf_dir))

        # Ako je prikazano 10 stranica, pitamo korisnika da li zeli jos
        if counter % 10 == 0:
            more = input('\n' + str(counter) + '/' + str(len(pages)) +
                         ' prikazano, da li zelite prikazati jos? Unesite kraj ako ne zelite: ')
            if more.lower() == 'kraj':
                break
            print()
        counter += 1

    # Ako ima manje od 5 rezultata, pitamo korisnika da li je mislio na neku drugu rec
    if counter < 5:
        print('Da li ste mislili:', end=' ')

        # Ako korisnik unese da, ponovo trazimo upit
        again = input(did_you_mean(query) + '? (da ako jeste): ')
        if again == 'da':
            query = did_you_mean(query)
            transformed_query, words = transform_query(query, graph)
            pages = page_rank(transformed_query, graph)

            counter = 1
            for page in pages:
                print(f'{counter}. Page {page.index()} - Score: {page.score()}')
                print(find_snippet(words, page.index(), pdf_dir))

                if counter % 10 == 0:
                    more = input('\n' + str(counter) + '/' + str(len(pages)) +
                                 ' prikazano, da li zelite prikazati jos? Unesite kraj ako ne zelite: ')
                    if more.lower() == 'kraj':
                        break
                    print()
                counter += 1

    # Pitamo korisnika da li zeli da sacuva rezultate
    save = input('Da li zelite da sacuvate rezultate? (da ako zelite): ')

    # Ako korisnik zeli da sacuva rezultate, pravimo pdf fajl
    if save == 'da':
        result = os.path.join('..', 'results', '(' + query + ')-' + pdf)
        create_pdf(pages, words, result, pdf)
