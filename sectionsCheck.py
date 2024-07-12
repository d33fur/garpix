import json
import re

def check_required_headers(json_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    elements = data['elements']
    pattern = re.compile(r'//Document/H1(?:\[(\d+)\])?')

    required_headers = [
        "содержание",
        "термины и определения",
        "перечень сокращений и обозначений",
        "введение",
        "заключение",
        "список использованных источников",
        "приложения"
    ]

    errors = []
    isCorrectOrder = False

    found_headers = []
    found_headers_lower = set()

    for element in elements:
        match = pattern.search(element['Path'])
        if match:
            header_text = element['Text'].strip()

            # check required
            if header_text.lower() in found_headers_lower:
                if header_text not in errors:
                    errors.append(header_text)
            elif header_text.lower() in [header.lower() for header in required_headers]:
                found_headers.append(header_text)
                found_headers_lower.add(header_text.lower())

    # order
    correct_order = True
    for i in range(len(found_headers) - 1):
        current_header = found_headers[i]
        next_header = found_headers[i + 1]
        current_index = required_headers.index(current_header.lower())
        next_index = required_headers.index(next_header.lower())
        if current_index > next_index:
            correct_order = False
            break

    if correct_order:
        isCorrectOrder = True

    missing_headers = [header for header in required_headers if header.lower() not in found_headers_lower]

    if missing_headers:
        for header in required_headers:
            if header.lower() in missing_headers:
                errors.append(header)

    return errors

def check_format(json_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    elements = data['elements']

    errors_ending_with_dot = []
    errors_not_lowercase = []
    errors_containing_underline = []
    errors_no_paragraph_indent = []
    errors_not_bold_font = []
    errors_wrong_font = []
    errors_wrong_font_size = []

    for element in elements:
        if 'Text' in element and element['Path'].startswith("//Document/H1"):
            header_text = element['Text'].strip()
            page_number = element['Page']
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
                errors_ending_with_dot.append(header_text)

            # lowercase
            if not header_text.isupper() and not (header_text[0].isupper() and not any(c.islower() for c in header_text)):
                errors_not_lowercase.append(header_text)

            # Underline
            if '_' in header_text:
                errors_containing_underline.append(header_text)

            # Indent
            if not has_paragraph_indent:
                errors_no_paragraph_indent.append(header_text)

            # Font type & bold
            font = element['Font']
            if "TimesNewRomanPS-BoldMT" not in font['name']:
                errors_not_bold_font.append(header_text)
            elif "family_name" in font and font["family_name"] == "Times New Roman PS":
                is_bold_font = True
            elif "family_name" in font and font["family_name"] != "Times New Roman PS":
                errors_wrong_font.append(header_text)

            # Font size
            expected_size = 16
            allowed_deviation = 1.0
            actual_size = element['TextSize']

            if not (expected_size - allowed_deviation <= actual_size <= expected_size + allowed_deviation):
                errors_wrong_font_size.append(header_text)

    return {
        "ending_with_dot": errors_ending_with_dot,
        "not_uppercase": errors_not_lowercase,
        "containing_underscore": errors_containing_underline,
        "no_paragraph_indent": errors_no_paragraph_indent,
        "not_bold_font": errors_not_bold_font,
        "wrong_font": errors_wrong_font,
        "wrong_font_size": errors_wrong_font_size
    }

def main():
    json_file = 'json/with/pdf/data'

    required_headers_errors = check_required_headers(json_file) # returns list of missing required headers
    format_errors = check_format(json_file) # returns two-dimensional list sorted by type of error

    # print("Ошибки в обязательных заголовках:\n")
    # if required_headers_errors:
    #     for error in required_headers_errors:
    #         print(f"- {error}")
    # else:
    #     print("Все есть.")

    # print("\nОшибки в форматировании заголовков:")
    # for aspect, errors in format_errors.items():
    #     if errors:
    #         print(f"\n{aspect.replace('_', ' ').capitalize()}:")
    #         for error in errors:
    #             print(f"- {error}")
    #     else:
    #         print(f"\n{aspect.replace('_', ' ').capitalize()}: Нет ошибок")

if __name__ == "__main__":
    main()