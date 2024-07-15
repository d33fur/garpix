import re
import json
import requests
import uuid
import os
from dotenv import load_dotenv

class JSONValidator:
    """
    Класс для проверки JSON файла, полученного из PDF документа.

    Атрибуты:
    CURRENT_PDF_JSON: pdf_to_json файл;
    CURRENT_STANDARD_JSON: стандарт госта;
    CURRENT_ERRORS_JSON: json файл, который содержит описание ошибок;
    all_errors_markdown: строка ошибок в виде markdown;
    all_errors: словарь всех ошибок;

    Методы:
    check_margins: проверяет документ на отступы;
    check_images: проверяет документ на оформление иллюстраций;
    general: проверка документа на то, что заголовки на разных страницах и проверка соответствия заголовков на страницах содержания и их фактических номеров страниц;
    check_tables: проверяет документ на оформление таблиц;
    check_titles: проверяет документ на критерии, связанные с оглавлением
    preferences: ...;
    check_appendices_format: ...;
    check_page_numbering: проверяет нумерацию страниц;
    check_font: ...;
    title_text_accordance: ...ж
    """
    def __init__(self, CURRENT_PDF_JSON, CURRENT_STANDARD_JSON, CURRENT_ERRORS_JSON):
        self.CURRENT_PDF_JSON = CURRENT_PDF_JSON
        self.CURRENT_STANDARD_JSON = CURRENT_STANDARD_JSON
        self.CURRENT_ERRORS_JSON = CURRENT_ERRORS_JSON
    
    def check_margins(self):
        mm2pt = 2.83464565
        def get_all_text_bounds():
            elements = self.CURRENT_PDF_JSON['elements']
            bds = []
            for elem in elements:
                if 'attributes' in elem and 'Bounds' in elem:
                    bds.append({
                        'bounds': elem['Bounds'],
                        'attributes': elem['attributes'],
                        'page': elem['Page']
                    })
            return bds


        def parse_value(value):
            # Extract numeric part and unit
            match = re.match(r"([0-9.]+)([a-z]+)", value, re.I)
            if match:
                value, unit = match.groups()
                value = float(value)
                if unit == 'mm':
                    return value * mm2pt
                elif unit == 'cm':
                    return value * 10 * mm2pt
            return 0

        bounds = get_all_text_bounds()
        settings = self.CURRENT_STANDARD_JSON['report_format']['margins']
        margins = {k: parse_value(v) for k, v in settings.items()}
        margins['right'] = 210 * mm2pt - margins['right']
        margins['top'] = 297 * mm2pt - margins['top']

        errors_desc = self.CURRENT_ERRORS_JSON['errors']
        found_errors = []
        prev_page = -1
        count = 0
        for element in bounds:
            if element['bounds'][0]-margins['left'] < -1:
                found_errors.append({
                    'error_desc': errors_desc[0]['description'],
                    'error_page': element['page'],
                    'error_text': None,
                })
            elif element['bounds'][2]-margins['right'] > 1:
                found_errors.append({
                    'error_desc': errors_desc[0]['description'],
                    'error_page': element['page'],
                    'error_text': None,
                })

            if prev_page != element['page']:
                prev_page = element['page']
                if abs(element['bounds'][1] - margins['top']) < 1:
                    print(element['bounds'][1], margins['top'])
                    found_errors.append({
                        'error_desc': errors_desc[0]['description'],
                        'error_page': element['page'],
                        'error_text': None,
                    })
                if prev_page >= 0:
                    if bounds[count-1]['bounds'][3] - margins['bottom'] < -1:
                        print(bounds[count-1]['bounds'][3], margins['bottom'])
                        found_errors.append({
                            'error_desc': errors_desc[0]['description'],
                            'error_page': element['page'],
                            'error_text': None,
                        })
            count += 1
        prev_page = -1
        to_del = []
        for element in found_errors:
            if element['error_page'] == prev_page:
                to_del.append(element)
            else:
                prev_page = element['error_page']
        for element in to_del:
            found_errors.remove(element)
        return found_errors
    
    def check_images(self):
        standard = dict()

        def parse_standard_json():
            standard['FontSize'] = re.findall(string=self.CURRENT_STANDARD_JSON['report_format']['font']['size'], pattern=r'(\d+)')[0]
            standard['FontType'] = ''.join(self.CURRENT_STANDARD_JSON['report_format']['font']['type'].split()) + "PSMT"
            standard['title_position'] = self.CURRENT_STANDARD_JSON['report_format']['illustrations']['title_position'].capitalize()
            standard['word'] = self.CURRENT_STANDARD_JSON['report_format']['illustrations']['reference_in_text']['word'].capitalize()

        parse_standard_json()

        elements = self.CURRENT_PDF_JSON['elements']
        pattern = re.compile(r'//Document/Figure(?:\[(\d+)\])?')

        # //Document/Figure(?:\[(\d+)\])?
        errors = list()

        for i in range(len(elements)):
            part = elements[i]
            match = pattern.search(part['Path'])
            if match and 'Text' not in part:
                print(part)
                # Проверяем на IndexError
                if i > 0 and i-1 < len(elements):
                    # Ищем ссылку в тексте на изображение
                    before_part = elements[i-1]
                    before_pattern = re.compile(f'см. {standard["word"]}. (\d+)(?:(.\d+)?)')
                    before_match = before_pattern.search(before_part['Text'])

                # Проверяем на IndexError
                if i > 0 and i+1 < len(elements):
                    # Ищем описание изображения
                    next_part = elements[i+1]
                    # Проверка если наткнулись на формулу
                    if part['Path'] == next_part['Path']:
                        continue
                    next_pattern = re.compile(f'{standard["word"]}. (\d+)(?:(.\d+. .*)?)')
                    if 'Text' in next_part:
                        next_match = next_pattern.search(next_part['Text'])
                    else: 
                        tmp = {
                            'error_desc': 'Нет описания для изображения.',
                            'error_page': next_part['Page']+1,
                            'error_text': None,
                        }
                        errors.append(tmp)
                        break

                if next_match and before_match:
                    # Проверка шрифтов и положения
                    next_part_align = next_part['attributes']['TextAlign']
                    next_part_font = next_part['Font']['name']
                    next_part_text_size = next_part['TextSize']

                    before_part_align = before_part['attributes']['TextAlign']
                    before_part_font = before_part['Font']['name']
                    before_part_text_size = before_part['TextSize']

                    if not (next_part_align == standard['title_position'] and standard['FontType'] in next_part_font and next_part_text_size == standard['FontSize']):
                        tmp = {
                            'error_desc': 'Проблема с шрифтом или позиционированием текста после изображением.',
                            'error_page': next_part['Page']+1,
                            'error_text': next_part['Text'],
                        }
                        errors.append(tmp)
                    if not (before_part_align == "Justify" and standard['FontType'] in before_part_font and before_part_text_size == standard['FontSize']):
                        tmp = {
                            'error_desc': 'Проблема с шрифтом или позиционированием текста перед изображением.',
                            'error_page': before_part['Page']+1,
                            'error_text': before_part['Text'],
                        }
                        errors.append(tmp)
                else: 
                    if not next_match:
                        tmp = {
                            'error_desc': 'Проблема с ссылкой или описанием изображения.',
                            'error_page': part['Page']+1,
                            'error_text': next_part['Text'],
                        }
                        errors.append(tmp)
                    if not before_match:
                        tmp = {
                            'error_desc': 'Проблема с ссылкой или описанием изображения.',
                            'error_page': part['Page']+1,
                            'error_text': before_part['Text'],
                        }
                        errors.append(tmp)

        return errors
    
    def general(self):
    # общий массив с ошибками
        errors = []
        def find_h1_headers(errors):
            elements = self.CURRENT_PDF_JSON['elements']
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
                        current_error['error_desc'] = 'Содержит несколько заголовков на одной странице.'
                        current_error['error_page'] = header['Page']
                        current_error['error_text'] = header['Text']
                        errors.append(current_error)
                        current_error = {}
                    pages_with_headers.add(header['Page'])

            check_headers_on_different_pages(headers, errors)
            # возвращает заголовки для других функций
            return headers

        def extract_header_entries(headers, errors):
            elements = self.CURRENT_PDF_JSON['elements']
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
                            current_error['error_desc'] = 'Заголовок должен быть на другой странице.'
                            current_error['error_page'] = header_entry['Page']
                            current_error['error_text'] = header_entry['Title']
                            errors.append(current_error)
                            current_error = {}
                    else:
                        current_error['error_desc'] = 'Заголовка нет в документе.'
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
    
    def check_tables(self):
        def get_all_text():
            elements = self.CURRENT_PDF_JSON['elements']
            text = []
            for i in range(len(self.CURRENT_PDF_JSON['pages'])):
                text.append('\n'.join(f"{element['Text']}" for element in elements if ('Page' in element and element['Page'] == i and 'Text' in element)))
            return text

        def check_title(title, found_errors, table):
            errors_desc = self.CURRENT_ERRORS_JSON['errors']
            settings = self.CURRENT_STANDARD_JSON['report_format']['tables']
            words = title.split()
            referenced_word = ''
            if 'capitalization' in settings['title_format']:
                if settings['title_format']['capitalization'] == 'first_letter':
                    referenced_word = 'Таблица'
                elif settings['title_format']['capitalization'] == 'all':
                    referenced_word = 'ТАБЛИЦА'
                elif settings['title_format']['capitalization'] == 'nothing':
                    referenced_word = 'таблица'

                if referenced_word not in words[0]:
                    found_errors.append({
                        'error_desc': errors_desc[21]['description'] + f'\n- Таблица {table["table_count"]}.',
                        'error_page': table['page'],
                        'error_text': None,
                    })
                    return

            if 'numbering' in settings:
                numb_set = settings['numbering']
                if numb_set['continuous'] and '.' not in words[1] and not (words[1].isdigit() and int(words[1]) != table['table_count']):
                    found_errors.append({
                        'error_desc': errors_desc[21]['description'] + f'\n- Таблица {table["table_count"]}.',
                        'error_page': table['page'],
                        'error_text': None,
                    })
                elif not numb_set['continuous'] and '.' not in words[1]:
                    found_errors.append({
                        'error_desc': errors_desc[21]['description'] + f'\n- Таблица {table["table_count"]}.',
                        'error_page': table['page'],
                        'error_text': None,
                    })
                if numb_set['per_section'] and '.' not in words[1] and not numb_set['continuous']:
                    found_errors.append({
                        'error_desc': errors_desc[21]['description'] + f'\n- Таблица {table["table_count"]}.',
                        'error_page': table['page'],
                        'error_text': None,
                    })
                elif numb_set['per_section'] and '.' in words[1]:
                    parts = words[1].split('.')
                    for part in parts:
                        if not part.isdigit():
                            found_errors.append({
                                'error_desc': errors_desc[21]['description'] + f'\n- Таблица {table["table_count"]}.',
                                'error_page': table['page'],
                                'error_text': None,
                            })

        def apply_table_settings():
            found_errors = []
            errors_desc = self.CURRENT_ERRORS_JSON['errors']
            settings = self.CURRENT_STANDARD_JSON['report_format']['tables']
            elements = self.CURRENT_PDF_JSON['elements']
            tables = []

            count = 0
            elem_num = 0
            for element in elements:
                if "//Document/Table" in element['Path'] and 'NumCol' in element['attributes']:
                    table_size = int(element['attributes']['NumCol'])*int(element['attributes']['NumRow'])
                    tables.append({
                        "elem_num": elem_num,
                        "page": element['Page'],
                        "table_count": count,
                        "table_start": element,
                        "table_size": table_size*2,
                        "prev_element": elements[elem_num-1 if elem_num-1 in elements else 0],
                        "next_element": elements[elem_num+table_size*2 if elem_num-1 in elements else 0]
                    })
                    count += 1
                elem_num += 1

            if 'top' in settings['title_position']:
                for table in tables:
                    if 'Text' not in table['prev_element']:
                        found_errors.append({
                            'error_desc': errors_desc[20]['description'] + f'\n- Таблица {table["table_count"]}.',
                            'error_page': table['page'],
                            'error_text': None,
                        })
                        continue
                    if 'left' in settings['title_position'] and table['prev_element']['Bounds'][0] > 100:
                        found_errors.append({
                            'error_desc': errors_desc[20]['description'] + f'\n- Таблица {table["table_count"]}.',
                            'error_page': table['page'],
                            'error_text': None,
                        })
                        continue
                    if 'right' in settings['title_position'] and table['prev_element']['Bounds'][0] < 100:
                        found_errors.append({
                            'error_desc': errors_desc[20]['description'] + f'\n- Таблица {table["table_count"]}.',
                            'error_page': table['page'],
                            'error_text': None,
                        })
                        continue
                    title = str(table['prev_element']['Text']) if table['prev_element']['Text'] else ''
                    check_title(title, found_errors, table)
            elif 'bottom' in settings['title_position']:
                for table in tables:
                    if 'Text' not in table['next_element']:
                        found_errors.append({
                            'error_desc': errors_desc[20]['description'] + f'\n- Таблица {table["table_count"]}.',
                            'error_page': table['page'],
                            'error_text': None,
                        })
                        continue
                    if 'left' in settings['title_position'] and table['next_element']['Bounds'][0] > 100:
                        found_errors.append({
                            'error_desc': errors_desc[20]['description'] + f'\n- Таблица {table["table_count"]}.',
                            'error_page': table['page'],
                            'error_text': None,
                        })
                        continue
                    if 'right' in settings['title_position'] and table['next_element']['Bounds'][0] < 100:
                        found_errors.append({
                            'error_desc': errors_desc[20]['description'] + f'\n- Таблица {table["table_count"]}.',
                            'error_page': table['page'],
                            'error_text': None,
                        })
                        continue
                    title = str(table['prev_element']['Text']) if table['next_element']['Text'] else ''
                    check_title(title, found_errors, table)

            for table in tables:
                if "//Document/Table" in table['next_element']['Path']:
                    found_errors.append({
                        'error_desc': errors_desc[18]['description'] + f'\n- Таблица {table["table_count"]}.',
                        'error_page': table['page'],
                        'error_text': None,
                    })

            if 'large_tables' in settings:
                for table in tables:
                    if "//Document/Table" in table['next_element']['Path'] and table['page'] != table['next_element']['page']:
                        found_errors.append({
                            'error_desc': errors_desc[0]['description'] + f'\n- Таблица {table["table_count"]}.',
                            'error_page': table['page'],
                            'error_text': None,
                        })
                        continue

            if 'object_position' in settings and 'after_next_page' in settings['object_position']:
                for table in tables:
                    if ('табл' not in all_text[table['page']]) or (table['page'] > 0 and 'табл' not in all_text[table['page']-1]):
                        found_errors.append({
                            'error_desc': errors_desc[19]['description'] + f'\n- Таблица {table["table_count"]}.',
                            'error_page': table['page'],
                            'error_text': None,
                        })
            elif 'object_position' in settings and 'after_first_reference' in settings['object_position']:
                for table in tables:
                    if 'табл' not in all_text[table['page']]:
                        found_errors.append({
                            'error_desc': errors_desc[19]['description'] + f'\n- Таблица {table["table_count"]}.',
                            'error_page': table['page'],
                            'error_text': None,
                        })
            return found_errors

        all_text = get_all_text()
        found_errors = apply_table_settings()
        return found_errors
    
    def preferences(self):

        def get_all_text():
            elements = self.CURRENT_PDF_JSON['elements']
            text = '\n'.join(f"{element['Text']}" for element in elements if 'Text' in element)
            return text

        all_text = get_all_text()
        errors_desc = self.CURRENT_ERRORS_JSON['errors']
        settings = self.CURRENT_STANDARD_JSON['report_format']['references']

        def get_ref_str(rs, num):
            if rs[0] == '[':
                return f'[{num}]'
            if rs[0] == '(':
                return f'({num})'

        results = []

        def find_all_overlapping_occurrences(text, substring):
            matches = re.finditer(f'(?={re.escape(substring)})', text)
            return [text[match.start():match.start() + len(substring)] for match in matches]

        last_found_ref = 0
        total_found = 0
        if 'numbering_style' in settings and settings['numbering_style'] == 'ARABIC':
            number = 0
            reference_string = '['
            if 'brackets' in settings and settings['brackets'] == 'ROUND_BRACKETS':
                reference_string = '('
            elif 'brackets' not in settings:
                return
            for i in range(100):
                target = get_ref_str(reference_string, i)
                res = find_all_overlapping_occurrences(all_text, target)
                if len(res) != 0:
                    last_found_ref = i
                    total_found += 1
                results.append(find_all_overlapping_occurrences(all_text, target))
        found_errors = []
        not_found = []
        if 'continuous_numbering' in settings and settings['continuous_numbering']:
            if last_found_ref != total_found:
                for i in range(last_found_ref):
                    if results[i] is []:
                        not_found.append(i)
            not_found_text = ', '.join(not_found)
            if not_found_text:
                found_errors.append({
                    'error_desc': errors_desc[34]['description'] + f'\n- Указания на {not_found_text}.',
                    'error_page': 0,
                    'error_text': None,
                })
        return found_errors
    
    def check_titles(self):
        
        def check_required_headers():
            elements = self.CURRENT_PDF_JSON['elements']
            pattern = re.compile(r'//Document/H1(?:\[(\d+)\])?')

            required_headers = self.CURRENT_STANDARD_JSON['report_format']['structural_elements']

            found_headers = []
            missing_headers = []

            # Check for found headers and determine the contents page
            contents_page = None
            for element in elements:
                match = pattern.search(element['Path'])
                if match:
                    header_text = element['Text'].strip()
                    found_headers.append(header_text)
                    if header_text.lower() == "содержание":
                        contents_page = element['Page'] + 1  # Adjust page number to start from 1

            # Check for missing headers
            for header in required_headers:
                if header.lower() not in [found_header.lower() for found_header in found_headers]:
                    # Find the first occurrence of the header in the elements list
                    page_number = None
                    for element in elements:
                        if 'Text' in element and element['Path'].startswith("//Document/H1"):
                            header_text = element['Text'].strip()
                            if header_text.lower() == header.lower():
                                page_number = element['Page'] + 1  # Adjust page number to start from 1
                                break

                    missing_headers.append({
                        'error_desc': 'Отсутсвует заголовок.',
                        'error_page': contents_page if contents_page else page_number,
                        'error_text': header
                    })

            return missing_headers

        def check_format():
            elements = self.CURRENT_PDF_JSON['elements']

            errors = []

            required_headers = self.CURRENT_STANDARD_JSON['report_format']['structural_elements']

            for element in elements:
                if 'Text' in element and element['Path'].startswith("//Document/H1"):
                    header_text = element['Text'].strip()
                    page_number = element['Page'] + 1  # Adjust page number to start from 1
                    has_paragraph_indent = False

                    if 'TextAlign' in element['attributes'] and element['attributes']['TextAlign'].lower() != self.CURRENT_STANDARD_JSON['report_format']['titles']['position'].lower():
                        errors.append({
                            'error_desc': 'Заголовок не по центру.',
                            'error_page': page_number,
                            'error_text': header_text
                        })
                    elif 'TextAlign' not in element['attributes']:
                        errors.append({
                            'error_desc': 'Заголовок не по центру.',
                            'error_page': page_number,
                            'error_text': header_text
                        })

                    if header_text.endswith('.') and not self.CURRENT_STANDARD_JSON['report_format']['titles']['end_with_period']:
                        errors.append({
                            'error_desc': 'Заголовок заканчивается точкой.',
                            'error_page': page_number,
                            'error_text': header_text
                        })

                    if header_text.upper() in required_headers:
                        if not header_text.isupper() and self.CURRENT_STANDARD_JSON['report_format']['titles']['capitalization'] == "all":
                            errors.append({
                                'error_desc': 'Не все буквы в заголовке - заглавные.',
                                'error_page': page_number,
                                'error_text': header_text
                            })
                    else:
                        words = header_text.split()
                        if words:
                            first_word = words[0]
                            if first_word[0].isdigit() and len(first_word) > 1:
                                if not words[1][0].isupper() and self.CURRENT_STANDARD_JSON['report_format']['titles']['sections_and_subsections']['capitalize_first_letter'] == True:
                                    errors.append({
                                        'error_desc': 'Заголовок написан неправильно.',
                                        'error_page': page_number,
                                        'error_text': header_text
                                    })
                            elif not first_word[0].isupper() and self.CURRENT_STANDARD_JSON['report_format']['titles']['sections_and_subsections']['capitalize_first_letter'] == True:
                                errors.append({
                                    'error_desc': 'Заголовок написан неправильно.',
                                    'error_page': page_number,
                                    'error_text': header_text
                                })

                    if '_' in header_text:
                        errors.append({
                            'error_desc': 'Заголовок содержит подчеркивание.',
                            'error_page': page_number,
                            'error_text': header_text
                        })

                    font = element.get('Font', {})
                    if "TimesNewRomanPS-BoldMT" not in font.get('name', '') and "family_name" in font and self.CURRENT_STANDARD_JSON['report_format']['font']['type'] not in font["family_name"]:
                        errors.append({
                            'error_desc': 'Заголовок не жирным шрифтом.',
                            'error_page': page_number,
                            'error_text': header_text
                        })
                    elif "family_name" in font and "family_name" in font and self.CURRENT_STANDARD_JSON['report_format']['font']['type'] not in font["family_name"]:
                        errors.append({
                            'error_desc': 'Загоровок неверным шрифтом.',
                            'error_page': page_number,
                            'error_text': header_text
                        })

                    expected_size = 16
                    allowed_deviation = 1.0
                    actual_size = element.get('TextSize', 0)

                    if not (expected_size - allowed_deviation <= actual_size <= expected_size + allowed_deviation):
                        errors.append({
                            'error_desc': 'Неверный размер шрифта заголовка.',
                            'error_page': page_number,
                            'error_text': header_text
                        })

            return errors

        feedback_of_required = check_required_headers()
        feedback_format = check_format()

        feedback_title = feedback_of_required + feedback_format

        return feedback_title
    
    def check_appendices_format(self):
        elements = self.CURRENT_PDF_JSON['elements']
        errors = []

        appendix_format = self.CURRENT_STANDARD_JSON['report_format']['appendices']
        allowed_letters = appendix_format['numbering']['allowed_letters']
        required_word = "приложени" # Расчет на случай, когда склонение неправильное

        appendix_pattern = re.compile(rf'{required_word}\s*([{allowed_letters}])', re.IGNORECASE)

        for element in elements:
            if 'Text' in element and element['Path'].startswith("//Document/H1"):
                header_text = element['Text']
                page_number = element['Page'] + 1

                if not re.search(required_word, header_text, re.IGNORECASE):
                    continue

                if 'прилож' in header_text.lower() and 'приложение' not in header_text.lower():
                    errors.append({
                        'error_desc': 'Приложение написано неверно.',
                        'error_page': page_number,
                        'error_text': header_text
                    })
                elif element['title_format']['word'] != header_text:
                    errors.append({
                        'error_desc': 'Неправильный формат приложения.',
                        'error_page': page_number,
                        'error_text': header_text
                    })

                match = appendix_pattern.match(header_text)
                if match:
                    letter = match.group(1).upper()
                    if letter not in allowed_letters:
                        errors.append({
                            'error_desc': f'Неверная буква в приложении: {letter}.',
                            'error_page': page_number,
                            'error_text': header_text
                        })
                else:
                    errors.append({
                        'error_desc': 'Неверный формат приложения.',
                        'error_page': page_number,
                        'error_text': header_text
                    })

        return errors

    # def check_page_numbering(self):
    #     error_message = []
    #     parametrs = self.CURRENT_STANDARD_JSON["report_format"]["page_numbering"]
    #     style = parametrs['style']
    #     position = parametrs['position']
    #     starting_page = parametrs['starting_page']
    #
    #     def generate_numbering(style, starting_page):
    #         page_count = self.CURRENT_PDF_JSON['extended_metadata']['page_count']
    #         match style:
    #             case 'ARABIC':
    #                 return list(map(str, range(starting_page, page_count + 1)))
    #             case _:
    #                 return []
    #
    #     def numbering_page_element(position):
    #         ans = []
    #         match position[0]:
    #             case 'Bottom':
    #                 previous_element = None
    #                 for element in self.CURRENT_PDF_JSON['elements']:
    #                     if element['Page'] == 0:
    #                         previous_element = element
    #                         continue
    #                     if element['Page'] != previous_element['Page']:
    #                         ans.append(previous_element)
    #                     previous_element = element
    #                 ans.append(previous_element)
    #                 return ans
    #             case _:
    #                 return []
    #
    #     numbering = generate_numbering(style, starting_page)
    #     for page_num, element in enumerate(numbering_page_element(position), 1):
    #         if page_num < starting_page:
    #             continue
    #         if "Text" in element:
    #             if element['Text'] != numbering[page_num - starting_page]:
    #                 error_message.append({'error_desc': 'Неправильная нумерации страницы. Должно быть ' + '"' +
    #                                                     numbering[page_num - starting_page] + '"',
    #                                       'error_page': element['Page'] + 1,
    #                                       'error_text': element['Text']})
    #             else:
    #                 if "TextAllign" in element['attributes']:
    #                     if element['attributes']['TextAllign'] != position[1]:
    #                         error_message.append({'error_desc': 'Неправильное расположение по ширине.',
    #                                               'error_page': element['Page'] + 1,
    #                                               'error_text': element['Text']})
    #                 else:
    #                     error_message.append({'error_desc': 'Неправильное расположение по ширине.',
    #                                           'error_page': element['Page'] + 1,
    #                                           'error_text': element['Text']})
    #
    #         else:
    #             error_message.append({'error_desc': 'Нет нумерации страницы.',
    #                                   'error_page': element['Page'] + 1,
    #                                   'error_text': None})
    #     return error_message

    def title_text_accordance(self):
        def get_env():
            file = "auth.env"
            if os.path.exists(file):
                load_dotenv(file)

        get_env()

        def get_access_token():
            request_id = uuid.uuid4()
            url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
            payload = 'scope=GIGACHAT_API_PERS'
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json',
                'RqUID': request_id.__str__(),
                'Authorization': f'Basic {os.environ.get("GIGACHAT_AUTH")}'
            }
            response = requests.request("POST", url, headers=headers, data=payload, verify=False)
            return response.json()['access_token']

        access_token = get_access_token()

        def get_all_text():
            elements = self.CURRENT_PDF_JSON['elements']
            headers = []
            element_pos = 0
            for element in elements:
                if '//Document/H1' in element['Path']:
                    headers.append({
                        'title': element['Text'],
                        'header_pos': element_pos,
                        'next_header_pos': -1,
                        'text': '',
                    })
                element_pos += 1
            if len(headers) == 0:
                return None
            for i in range(len(headers) - 1):
                headers[i]['next_header_pos'] = headers[i + 1]['header_pos']
            element_pos = 0
            cur_header = 0
            for element in elements:
                if element_pos > headers[cur_header]['header_pos']:
                    if element_pos < headers[cur_header]['next_header_pos'] or headers[cur_header][
                        'next_header_pos'] == -1:
                        if 'Text' in element:
                            headers[cur_header]['text'] += element['Text']
                    else:
                        cur_header = cur_header + 1
                        if cur_header >= len(headers):
                            break
                element_pos += 1
            return headers

        def send_evaluation_request(title, text):
            url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
            payload = json.dumps({
                "model": "GigaChat",
                "messages": [
                    {
                        "role": "user",
                        "content": f"Оцени от 0 до 100, насколько текст подходит заголовку. Выведи цифру. Заголовок: {title}. Текст: {text}"
                    }
                ],
                "stream": False,
                "repetition_penalty": 1
            })
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': f'Bearer {access_token}'
            }
            response = requests.request("POST", url, headers=headers, data=payload, verify=False)
            return response.json()["choices"][0]["message"]["content"]

        hds = get_all_text()
        found_errors = []
        errors_desc = self.CURRENT_ERRORS_JSON['errors']
        for header in hds:
            eval = send_evaluation_request(header['title'], header['text'])
            if eval.isdigit():
                if int(eval) < 50:
                    found_errors.append(errors_desc[8]['description'] + f'\n- заголовок {header["title"]}')
        return found_errors


    def check_font(self):  
        section_titles = [
        "СПИСОК ИСПОЛНИТЕЛЕЙ",
        "РЕФЕРАТ",
        "СОДЕРЖАНИЕ",
        "ТЕРМИНЫ И ОПРЕДЕЛЕНИЯ",
        "ПЕРЕЧЕНЬ СОКРАЩЕНИЙ И ОБОЗНАЧЕНИЙ",
        "ВВЕДЕНИЕ",
        "ЗАКЛЮЧЕНИЕ",
        "СПИСОК ИСПОЛЬЗОВАННЫХ ИСТОЧНИКОВ",
        "ПРИЛОЖЕНИЕ"]
        error_message = []
        parametrs = self.CURRENT_STANDARD_JSON["report_format"]["font"]
        color = parametrs['color']
        min_size = int(parametrs['min_size'])
        fontname = parametrs['default_type']
        bold_text_types = parametrs['bold']['apply_to']
        italic_text_types = parametrs['italic']['apply_to']

        def is_text(element):
            return "Font" in element
        
        def is_correct_font(text,fontname):
            return fontname in text['Font']['family_name']
        
        def is_bold(text):
            fontname = text['Font']['name']
            return 'Bold' in fontname

        def is_italic(text):
            fontname = text['Font']['name']
            return 'Italic' in fontname

        def check_color(color):
            error_message = []
            return error_message
        
        def check_font_size(min_size):
            error_message = []
            current_page = -1
            epsilon = 0.1
            for element in self.CURRENT_PDF_JSON['elements']:
                if is_text(element):
                    if element['TextSize'] < (min_size - epsilon):
                        if current_page != element['Page']:
                            error_message.append({'error_desc':'Размер шрифта меньше необходимых ' + str(min_size) + 'pt.',
                                                'error_page': element['Page'] + 1,
                                                'error_text': element['Text'] })
                    current_page = element['Page']
            return error_message

        def check_font_type(fontname):
            error_message = []
            heauristic_ratio = 0.9
            text_length = 0.0
            conventional_text_length = 0.0
            for element in self.CURRENT_PDF_JSON['elements']:
                if is_text(element):
                    text_length += len(element['Text'])
                    if is_correct_font(element,fontname):
                        conventional_text_length += len(element['Text'])
            if (conventional_text_length / text_length) < heauristic_ratio:
                error_message.append({'error_desc':'Использованный в документе шрифт не соответствует ' + str(fontname) + '.',
                                    'error_page': None,
                                    'error_text': element['Text']})
            return error_message

        def check_bold(bold_text_types):
            error_message = []
            for category in bold_text_types:
                if category == 'section_titles':
                    for element in self.CURRENT_PDF_JSON['elements']:
                        if is_text(element):
                            if element['Text'] in section_titles and not is_bold(element):
                                error_message.append({'error_desc':'Заголовок структурного элемента \'' + category + '\' не выделен полужирном шрифтом.',
                                                    'error_page': element['Page'] + 1,
                                                    'error_text': element['Text']})
            return error_message

        def check_italic(italic_text_types):
            error_message = []
            for category in italic_text_types:
                if category == 'terms_in_latin':
                    for element in self.CURRENT_PDF_JSON['elements']:
                        if is_text(element) and "Lang" in element:
                            if (element['Lang'] == 'ru') and is_italic(element):
                                error_message.append({'error_desc':'Текст не должен быть выделен курсивом.',
                                                    'error_page': element['Page'] + 1,
                                                    'error_text': element['Text']})
            return error_message
    
        error_message = (check_color(color)+
            check_font_size(min_size)+
            check_font_type(fontname)+
            check_bold(bold_text_types)+
            check_italic(italic_text_types))
        return error_message
    
    def collect_errors(self):
        all_errors = list()
        method_list = [func for func in dir(JSONValidator) if callable(getattr(JSONValidator, func)) and not func.startswith("__") and not func == "collect_errors"]
        for i in method_list:
            method = getattr(self, i)
            all_errors += method()
        return all_errors    

    @property
    def all_errors_markdown(self):
        errors = self.collect_errors()
        formatted_errors = [f"{error['error_desc']} Cтраница {error['error_page']}. Текст из документа: \n\n```{error['error_text']}```\n\n" for error in errors]
        result_string = '\n'.join(formatted_errors)
        return result_string
    
    @property
    def all_errors(self):
        return self.collect_errors()

