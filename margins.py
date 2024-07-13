def margins():
    import json

    mm2pt = 2.83464565

    def get_all_text_bounds():
        elements = CURRENT_PDF_JSON['elements']
        bds = []
        for elem in elements:
            if 'attributes' in elem and 'Bounds' in elem:
                bds.append({
                    'bounds': elem['Bounds'],
                    'attributes': elem['attributes'],
                    'page': elem['Page']
                })
        return bds

    import re

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
    settings = CURRENT_STANDARD_JSON['report_format']['margins']
    margins = {k: parse_value(v) for k, v in settings.items()}
    margins['right'] = 210 * mm2pt - margins['right']
    margins['top'] = 297 * mm2pt - margins['top']

    errors_desc = CURRENT_ERRORS_JSON['errors']
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