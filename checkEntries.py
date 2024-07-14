import json
import re


with open('./structuredData.json', 'r') as f:
    CURRENT_PDF_JSON = json.load(f)


def general():
    # общий массив с ошибками
    errors = []
    def find_h1_headers(errors):
        elements = CURRENT_PDF_JSON['elements']
        pattern = re.compile(r'//Document/H1(?:\[(\d+)\])?')

        headers = []
        for element in elements:
            if 'Path' in element and pattern.match(element['Path']):
                header = {
                    'Text': element['Text'].strip(),
                    'Page': element['Page'] + 1
                }
                headers.append(header)

        # # для проверки
        # print("H1 Headers:")
        # for header in headers:
        #     print(header)

        def check_headers_on_different_pages(headers, errors):
            pages_with_headers = set()
            current_error = {}

            for header in headers:
                if header['Page'] in pages_with_headers:
                    current_error['error_desc'] = 'contains multiple H1 headers on one page.'
                    current_error['error_page'] = header['Page']
                    current_error['error_text'] = header['Text']
                    errors.append(current_error)
                    current_error = {}
                pages_with_headers.add(header['Page'])

        check_headers_on_different_pages(headers, errors)
        # возвращает заголовки для других функций
        return headers

    def extract_header_entries(headers, errors):
        elements = CURRENT_PDF_JSON['elements']
        header_pattern = re.compile(r'//Document/TOC/TOCI(?:\[\d+\])?/Reference')
        # паттерн для введения тк у него другой Path
        temp_pattern = re.compile(r'//Document/TOC/TOCI(?:\[\d+\])?/Span/Reference')

        header_entries = []
        current_entry = {}

        for element in elements:
            if 'Path' in element and (header_pattern.match(element['Path']) or temp_pattern.match(element['Path'])):
                if 'Lbl' in element['Path']:
                    current_entry['Number'] = element['Text'].strip()
                elif 'LBody' in element['Path']:
                    # проверяем является ли подзаголовком (если да, тогда просто не записываем)
                    if re.search(r'\.\d+', current_entry['Number']):
                        current_entry = {}
                        continue
                    header_text = element['Text'].strip()
                    header_page = int(re.search(r'\d+$', header_text).group())
                    # удаляем точки и лишние пробелы из названия
                    header_title = re.sub(r'\s*\.\s*\d+\s*$', '', header_text).strip()
                    header_title = re.sub(r'\.\.+', '', header_title).strip()
                    current_entry['Title'] = current_entry['Number'] + ' ' + header_title
                    current_entry['Page'] = header_page
                    header_entries.append(current_entry)
                    current_entry = {}
                # отдельный случай для Введения тк у него другой Path
                else:
                    header_text = element['Text'].strip()
                    header_page = int(re.search(r'\d+$', header_text).group())
                    # удаляем точки и лишние пробелы из названия
                    header_title = re.sub(r'\s*\.\s*\d+\s*$', '', header_text).strip()
                    header_title = re.sub(r'\.\.+', '', header_title).strip()
                    current_entry['Title'] = header_title
                    current_entry['Page'] = header_page
                    header_entries.append(current_entry)
                    current_entry = {}

        # # для проверки
        # print("\nHeader Entries:")
        # for entry in header_entries:
        #     print(entry)


        def check_headers_with_entries(headers, headers_entries, errors):
            current_error = {}

            for header_entry in headers_entries:
                matched_header = next((header for header in headers if header_entry['Title'] in header['Text']), None)
                if matched_header:
                    if header_entry['Page'] != matched_header['Page']:
                        current_error['error_desc'] = 'H1 header should be on other page.'
                        current_error['error_page'] = header_entry['Page']
                        current_error['error_text'] = header_entry['Title']
                        errors.append(current_error)
                        current_error = {}
                else:
                    current_error['error_desc'] = 'does not match any header in the document.'
                    current_error['error_page'] = header_entry['Page']
                    current_error['error_text'] = header_entry['Title']
                    errors.append(current_error)
                    current_error = {}

        check_headers_with_entries(headers, header_entries, errors)

    # запускает функции для обработки заголовков
    headers = find_h1_headers(errors)
    extract_header_entries(headers, errors)

    # возвращает массив ошибок
    return errors

def main():
    json_file = './structuredData.json'

    errors = general()

    if errors:
        print("\nErrors found:")
        for error in errors:
            print(f"- {error}")
    else:
        print("ALl GOOD")


if __name__ == "__main__":
    main()
