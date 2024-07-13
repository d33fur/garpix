import json
import re

def check_required_headers(json_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    elements = data['elements']
    pattern = re.compile(r'//Document/H1(?:\[(\d+)\])?')

    required_headers = [
        "СОДЕРЖАНИЕ",
        "ТЕРМИНЫ И ОПРЕДЕЛЕНИЯ",
        "ПЕРЕЧЕНЬ СОКРАЩЕНИЙ И ОБОЗНАЧЕНИЙ",
        "ВВЕДЕНИЕ",
        "ЗАКЛЮЧЕНИЕ",
        "СПИСОК ИСПОЛЬЗОВАННЫХ ИСТОЧНИКОВ",
        "ПРИЛОЖЕНИЯ"
    ]

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
                'error_desc': 'Missing required header',
                'error_page': contents_page if contents_page else page_number,
                'error_text': header
            })

    return missing_headers

def check_format(json_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    elements = data['elements']

    errors = []

    required_headers = [
        "СОДЕРЖАНИЕ",
        "ТЕРМИНЫ И ОПРЕДЕЛЕНИЯ",
        "ПЕРЕЧЕНЬ СОКРАЩЕНИЙ И ОБОЗНАЧЕНИЙ",
        "ВВЕДЕНИЕ",
        "ЗАКЛЮЧЕНИЕ",
        "СПИСОК ИСПОЛЬЗОВАННЫХ ИСТОЧНИКОВ",
        "ПРИЛОЖЕНИЯ"
    ]

    for element in elements:
        if 'Text' in element and element['Path'].startswith("//Document/H1"):
            header_text = element['Text'].strip()
            page_number = element['Page'] + 1  # Adjust page number to start from 1
            has_paragraph_indent = False
            is_bold_font = False
            correct_font_family = False

            if 'Bounds' in element:
                bounds = element['Bounds']
                if len(bounds) == 4:
                    left_x = bounds[0] * 0.0264583333 
                    if left_x > 3:
                        has_paragraph_indent = True

            if header_text.endswith('.'):
                errors.append({
                    'error_desc': 'Header ends with a dot',
                    'error_page': page_number,
                    'error_text': header_text
                })

            if header_text.upper() in required_headers:
                if not header_text.isupper():
                    errors.append({
                        'error_desc': 'Header not fully uppercase',
                        'error_page': page_number,
                        'error_text': header_text
                    })
            else:
                words = header_text.split()
                if words:
                    first_word = words[0]
                    if first_word[0].isdigit() and len(first_word) > 1:
                        if not words[1][0].isupper():
                            errors.append({
                                'error_desc': 'Header not capitalized properly',
                                'error_page': page_number,
                                'error_text': header_text
                            })
                    elif not first_word[0].isupper():
                        errors.append({
                            'error_desc': 'Header not capitalized properly',
                            'error_page': page_number,
                            'error_text': header_text
                        })

            if '_' in header_text:
                errors.append({
                    'error_desc': 'Header contains underscore',
                    'error_page': page_number,
                    'error_text': header_text
                })

            if not has_paragraph_indent:
                errors.append({
                    'error_desc': 'Header lacks paragraph indent',
                    'error_page': page_number,
                    'error_text': header_text
                })

            font = element.get('Font', {})
            if "TimesNewRomanPS-BoldMT" not in font.get('name', '') and "family_name" in font and font["family_name"] == "Times New Roman PS":
                errors.append({
                    'error_desc': 'Header not in bold font',
                    'error_page': page_number,
                    'error_text': header_text
                })
            elif "family_name" in font and font["family_name"] != "Times New Roman PS":
                errors.append({
                    'error_desc': 'Header in wrong font',
                    'error_page': page_number,
                    'error_text': header_text
                })

            expected_size = 16
            allowed_deviation = 1.0
            actual_size = element.get('TextSize', 0)

            if not (expected_size - allowed_deviation <= actual_size <= expected_size + allowed_deviation):
                errors.append({
                    'error_desc': 'Header has incorrect font size',
                    'error_page': page_number,
                    'error_text': header_text
                })

    return errors