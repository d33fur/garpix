def preferences():
    import json

    def get_all_text():
        elements = CURRENT_PDF_JSON['elements']
        text = '\n'.join(f"{element['Text']}" for element in elements if 'Text' in element)
        return text

    all_text = get_all_text()
    errors_desc = CURRENT_ERRORS_JSON['errors']
    settings = CURRENT_STANDARD_JSON['report_format']['references']

    def get_ref_str(rs, num):
        if rs[0] == '[':
            return f'[{num}]'
        if rs[0] == '(':
            return f'({num})'

    results = []
    import re

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
                'error_desc': errors_desc[34]['description'] + f'\n- указания на {not_found_text}',
                'error_page': 0,
                'error_text': None,
            })
    return found_errors