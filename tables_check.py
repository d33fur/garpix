def tables_check():
    def get_all_text():
        elements = CURRENT_PDF_JSON['elements']
        text = []
        for i in range(len(CURRENT_PDF_JSON['pages'])):
            text.append('\n'.join(f"{element['Text']}" for element in elements if ('Page' in element and element['Page'] == i and 'Text' in element)))
        return text

    def check_title(title, found_errors, table):
        errors_desc = CURRENT_ERRORS_JSON['errors']
        settings = CURRENT_STANDARD_JSON['report_format']['tables']
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
                    'error_desc': errors_desc[21]['description'] + f'\n- таблица {table['table_count']}',
                    'error_page': table['page'],
                    'error_text': None,
                })
                return

        if 'numbering' in settings:
            numb_set = settings['numbering']
            if numb_set['continuous'] and '.' not in words[1] and not (words[1].isdigit() and int(words[1]) != table['table_count']):
                found_errors.append({
                    'error_desc': errors_desc[21]['description'] + f'\n- таблица {table['table_count']}',
                    'error_page': table['page'],
                    'error_text': None,
                })
            elif not numb_set['continuous'] and '.' not in words[1]:
                found_errors.append({
                    'error_desc': errors_desc[21]['description'] + f'\n- таблица {table['table_count']}',
                    'error_page': table['page'],
                    'error_text': None,
                })
            if numb_set['per_section'] and '.' not in words[1] and not numb_set['continuous']:
                found_errors.append({
                    'error_desc': errors_desc[21]['description'] + f'\n- таблица {table['table_count']}',
                    'error_page': table['page'],
                    'error_text': None,
                })
            elif numb_set['per_section'] and '.' in words[1]:
                parts = words[1].split('.')
                for part in parts:
                    if not part.isdigit():
                        found_errors.append({
                            'error_desc': errors_desc[21]['description'] + f'\n- таблица {table['table_count']}',
                            'error_page': table['page'],
                            'error_text': None,
                        })

    def apply_table_settings():
        found_errors = []
        errors_desc = CURRENT_ERRORS_JSON['errors']
        settings = CURRENT_STANDARD_JSON['report_format']['tables']
        elements = CURRENT_PDF_JSON['elements']
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
                        'error_desc': errors_desc[20]['description'] + f'\n- таблица {table['table_count']}',
                        'error_page': table['page'],
                        'error_text': None,
                    })
                    continue
                if 'left' in settings['title_position'] and table['prev_element']['Bounds'][0] > 100:
                    found_errors.append({
                        'error_desc': errors_desc[20]['description'] + f'\n- таблица {table['table_count']}',
                        'error_page': table['page'],
                        'error_text': None,
                    })
                    continue
                if 'right' in settings['title_position'] and table['prev_element']['Bounds'][0] < 100:
                    found_errors.append({
                        'error_desc': errors_desc[20]['description'] + f'\n- таблица {table['table_count']}',
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
                        'error_desc': errors_desc[20]['description'] + f'\n- таблица {table['table_count']}',
                        'error_page': table['page'],
                        'error_text': None,
                    })
                    continue
                if 'left' in settings['title_position'] and table['next_element']['Bounds'][0] > 100:
                    found_errors.append({
                        'error_desc': errors_desc[20]['description'] + f'\n- таблица {table['table_count']}',
                        'error_page': table['page'],
                        'error_text': None,
                    })
                    continue
                if 'right' in settings['title_position'] and table['next_element']['Bounds'][0] < 100:
                    found_errors.append({
                        'error_desc': errors_desc[20]['description'] + f'\n- таблица {table['table_count']}',
                        'error_page': table['page'],
                        'error_text': None,
                    })
                    continue
                title = str(table['prev_element']['Text']) if table['next_element']['Text'] else ''
                check_title(title, found_errors, table)

        for table in tables:
            if "//Document/Table" in table['next_element']['Path']:
                found_errors.append({
                    'error_desc': errors_desc[18]['description'] + f'\n- таблица {table['table_count']}',
                    'error_page': table['page'],
                    'error_text': None,
                })

        if 'large_tables' in settings:
            for table in tables:
                if "//Document/Table" in table['next_element']['Path'] and table['page'] != table['next_element']['page']:
                    found_errors.append({
                        'error_desc': errors_desc[0]['description'] + f'\n- таблица {table['table_count']}',
                        'error_page': table['page'],
                        'error_text': None,
                    })
                    continue

        if 'object_position' in settings and 'after_next_page' in settings['object_position']:
            for table in tables:
                if ('табл' not in all_text[table['page']]) or (table['page'] > 0 and 'табл' not in all_text[table['page']-1]):
                    found_errors.append({
                        'error_desc': errors_desc[19]['description'] + f'\n- таблица {table['table_count']}',
                        'error_page': table['page'],
                        'error_text': None,
                    })
        elif 'object_position' in settings and 'after_first_reference' in settings['object_position']:
            for table in tables:
                if 'табл' not in all_text[table['page']]:
                    found_errors.append({
                        'error_desc': errors_desc[19]['description'] + f'\n- таблица {table['table_count']}',
                        'error_page': table['page'],
                        'error_text': None,
                    })
        return found_errors

    all_text = get_all_text()
    found_errors = apply_table_settings()
    return found_errors