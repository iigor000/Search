import os
import pdfplumber


def read_results_from_files(root):
    filenames = os.listdir(root)
    result = {}
    for filename in filenames:
        content = read_results_from_file(os.path.join(root, filename)).decode('utf-8')
        try:
            page_number = int(content[:content.index('\n')].split()[-1])
        except:
            try:
                page_number = int(content[:content.index('\n')].split()[0])
            except:
                page_number = None
        index = filename.split(".")[0]
        result[index] = {'index': index,
                         'page_number': page_number,
                         'content': content}
    return result


def read_results_from_file(path):
    with open(path, 'rb') as file:
        return file.read()


def print_dict(dict):
    for key in dict:
        page = dict[key]
        print('Index: %s' % key)
        print('Page number: %s' % page['page_number'])
        print('Content:\n\n' + page['content'])
        print('\n\n\n')


def pdf_to_text_files(pdf_file):
    base_name = os.path.basename(pdf_file).split('.')[0]
    path = os.path.join('..', 'txts', base_name)
    os.makedirs(path, exist_ok=True)

    with pdfplumber.open(pdf_file) as pdf:
        for page_num, page in enumerate(pdf.pages):
            text = page.extract_text()

            with open(os.path.join(path, f'{page_num}.txt'), 'w', encoding='utf-8') as f:
                f.write(text)


if __name__ == '__main__':
    in_path = '../pdf/proj.pdf'
    out_path = '../txts/example'
    results = read_results_from_files(out_path)
    pdf_to_text_files(in_path)
