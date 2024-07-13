import json
import re


def find_h1_headers(json_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    elements = data['elements']
    pattern = re.compile(r'//Document/H1(?:\[(\d+)\])?')

    headers = []
    for element in elements:
        if 'Path' in element and pattern.match(element['Path']):
            header = {
                'Text': element['Text'].strip(),
                'Page': element['Page'] + 1
            }
            headers.append(header)

    return headers


def check_headers_on_different_pages(headers):
    pages_with_headers = set()
    errors = []

    for header in headers:
        if header['Page'] in pages_with_headers:
            errors.append(f"Page {header['Page']} contains multiple H1 headers.")
        pages_with_headers.add(header['Page'])

    return errors


def extract_header_entries(json_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    elements = data['elements']
    header_pattern = re.compile(r'//Document/TOC/TOCI(?:\[\d+\])?/Reference')
    # паттерн для введения тк у него другой Path
    temp_pattern = re.compile(r'//Document/TOC/TOCI/Span/Reference')

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

    return header_entries


def check_headers_with_entries(headers, headers_entries):
    errors = []

    for header_entry in headers_entries:
        matched_header = next((header for header in headers if header_entry['Title'] in header['Text']), None)
        if matched_header:
            if header_entry['Page'] != matched_header['Page']:
                errors.append(f"Header '{header_entry['Title']}' is on page {matched_header['Page']}, but should be on page {header_entry['Page']}.")
        else:
            errors.append(f"header entry '{header_entry['Title']}' does not match any header in the document.")

    return errors


def main():
    json_file = '/Users/master/Downloads/structuredData.json'

    headers = find_h1_headers(json_file)
    page_errors = check_headers_on_different_pages(headers)

    # print("H1 Headers:")
    # for header in headers:
    #     print(header)

    header_entries = extract_header_entries(json_file)
    entries_errors = check_headers_with_entries(headers, header_entries)

    # print("\nHeader Entries:")
    # for entry in header_entries:
    #     print(entry)

    if page_errors:
        print("\nErrors found:")
        for error in page_errors:
            print(f"- {error}")
    else:
        print("All H1 headers are on separate pages.")

    if entries_errors:
        print("\nErrors found:")
        for error in entries_errors:
            print(f"- {error}")
    else:
        print("All H1 headers are on the right pages.")


if __name__ == "__main__":
    main()
