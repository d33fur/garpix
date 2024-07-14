import json
import re

with open('structuredData.json', 'r') as f:
    CURRENT_PDF_JSON = json.load(f)

with open('errors_desc.json', 'r') as f:
    CURRENT_ERRORS_JSON = json.load(f)

with open('7.32-2017.json', 'r') as f:
    CURRENT_STANDARD_JSON = json.load(f)

def check_titles():
    def Merge(dict1, dict2):
        res = {**dict1, **dict2}
        return res
    
    def check_required_headers():
        elements = CURRENT_PDF_JSON['elements']
        pattern = re.compile(r'//Document/H1(?:\[(\d+)\])?')

        required_headers = CURRENT_STANDARD_JSON['report_format']['structural_elements']

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

    def check_format():
        elements = CURRENT_PDF_JSON['elements']

        errors = []

        required_headers = CURRENT_STANDARD_JSON['report_format']['structural_elements']

        for element in elements:
            if 'Text' in element and element['Path'].startswith("//Document/H1"):
                header_text = element['Text'].strip()
                page_number = element['Page'] + 1  # Adjust page number to start from 1
                has_paragraph_indent = False

                if 'TextAlign' in element['attributes'] and element['attributes']['TextAlign'].lower() != CURRENT_STANDARD_JSON['report_format']['titles']['position'].lower():
                    errors.append({
                        'error_desc': 'Title not centered',
                        'error_page': page_number,
                        'error_text': header_text
                    })
                elif 'TextAlign' not in element['attributes']:
                    errors.append({
                        'error_desc': 'Title not centered',
                        'error_page': page_number,
                        'error_text': header_text
                    })

                if header_text.endswith('.') and not CURRENT_STANDARD_JSON['report_format']['titles']['end_with_period']:
                    errors.append({
                        'error_desc': 'Header ends with a dot',
                        'error_page': page_number,
                        'error_text': header_text
                    })

                if header_text.upper() in required_headers:
                    if not header_text.isupper() and CURRENT_STANDARD_JSON['report_format']['titles']['capitalization'] == "all":
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
                            if not words[1][0].isupper() and CURRENT_STANDARD_JSON['report_format']['titles']['sections_and_subsections']['capitalize_first_letter'] == True:
                                errors.append({
                                    'error_desc': 'Header not capitalized properly',
                                    'error_page': page_number,
                                    'error_text': header_text
                                })
                        elif not first_word[0].isupper() and CURRENT_STANDARD_JSON['report_format']['titles']['sections_and_subsections']['capitalize_first_letter'] == True:
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

                font = element.get('Font', {})
                if "TimesNewRomanPS-BoldMT" not in font.get('name', '') and "family_name" in font and CURRENT_STANDARD_JSON['report_format']['font']['type'] not in font["family_name"]:
                    errors.append({
                        'error_desc': 'Header not in bold font',
                        'error_page': page_number,
                        'error_text': header_text
                    })
                elif "family_name" in font and "family_name" in font and CURRENT_STANDARD_JSON['report_format']['font']['type'] not in font["family_name"]:
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

    feedback_of_required = check_required_headers()
    feedback_format = check_format()

    feedback_title = feedback_of_required + feedback_format

    return feedback_title