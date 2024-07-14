import json
import re

with open('structuredData.json', 'r') as f:
    CURRENT_PDF_JSON = json.load(f)

with open('errors_desc.json', 'r') as f:
    CURRENT_ERRORS_JSON = json.load(f)

with open('7.32-2017.json', 'r') as f:
    CURRENT_STANDARD_JSON = json.load(f)

def check_appendices_format():
    elements = CURRENT_PDF_JSON['elements']
    errors = []

    appendix_format = CURRENT_STANDARD_JSON['report_format']['appendices']
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
                    'error_desc': 'Appendix header is written incorrectly',
                    'error_page': page_number,
                    'error_text': header_text
                })
            elif element['title_format']['word'] != header_text:
                errors.append({
                    'error_desc': 'Appendix header case is incorrect',
                    'error_page': page_number,
                    'error_text': header_text
                })

            match = appendix_pattern.match(header_text)
            if match:
                letter = match.group(1).upper()
                if letter not in allowed_letters:
                    errors.append({
                        'error_desc': f'Appendix header contains invalid letter: {letter}',
                        'error_page': page_number,
                        'error_text': header_text
                    })
            else:
                errors.append({
                    'error_desc': 'Appendix header format incorrect',
                    'error_page': page_number,
                    'error_text': header_text
                })

    return errors