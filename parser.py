import pdfplumber
import re

def points_to_cm(points):
    inches = points / 72 
    cm = inches * 2.54   
    return cm 

def get_line_height(line):
    # Высота строки в точках
    line_height = line['bottom'] - line['top']
    return line_height

def get_expected_line_spacing(line_height):
    # Коэффициент, на который меньше нижний регистр по высоте
    lowercase_height_ratio = 0.7  # Примерный коэффициент для нижнего регистра

    # Ожидаемый промежуток между строками
    expected_spacing = line_height * 1.5 * lowercase_height_ratio
    return expected_spacing

def clean_font_name(fontname):
    return re.sub(r'^[A-Z]{6}\+', '', fontname)

def get_margins_and_paragraphs(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        page_data = []
        for page_num, page in enumerate(pdf.pages):
            page_dict = {
                'page_num': page_num,
                'width': page.width,
                'height': page.height,
                'margins': {
                    'top': page.height,
                    'bottom': page.height,
                    'left': page.width,
                    'right': page.width
                },
                'paragraphs': []
            }

            # Извлечение текста с координатами строк и шрифтом
            text_lines = page.extract_words(extra_attrs=["fontname"])

            # Первичный проход для определения общего левого отступа
            for line in text_lines:
                line['fontname'] = clean_font_name(line['fontname'])  # Очистка имени шрифта
                x0, y0, x1, y1 = line['x0'], line['top'], line['x1'], line['bottom']

                # Обновление отступов
                if y0 < page_dict['margins']['top']:
                    page_dict['margins']['top'] = y0
                if page.height - y1 < page_dict['margins']['bottom'] and page.height - y1 > 0:
                    page_dict['margins']['bottom'] = page.height - y1
                if x0 < page_dict['margins']['left']:
                    page_dict['margins']['left'] = x0
                if page.width - x1 < page_dict['margins']['right']:
                    page_dict['margins']['right'] = page.width - x1

            # Вторичный проход для определения абзацев (отступ сверху)
            current_paragraph = []
            previous_bottom = None
            previous_font = None
            for line in text_lines:
                x0, y0, x1, y1 = line['x0'], line['top'], line['x1'], line['bottom']
                fontname = line['fontname']

                line_height = y1 - y0
                expected_spacing = get_expected_line_spacing(line_height)

                if previous_bottom is None or y0 - previous_bottom > expected_spacing or fontname != previous_font:
                    if current_paragraph:
                        page_dict['paragraphs'].append(current_paragraph)
                    current_paragraph = []

                current_paragraph.append(line)
                previous_bottom = y1
                previous_font = fontname

            if current_paragraph:
                page_dict['paragraphs'].append(current_paragraph)

            # # Вторичный проход для определения абзацев (красная строка)
            # current_paragraph = []
            # prev_text = ""
            # for line in text_lines:
            #     x0, y0, x1, y1 = line['x0'], line['top'], line['x1'], line['bottom']
            #
            #     # Проверка на начало нового абзаца
            #     if x0 > page_dict['margins']['left']:
            #         if current_paragraph:
            #             page_dict['paragraphs'].append(current_paragraph)
            #             current_paragraph = []
            #         current_paragraph.append(line)
            #     else:
            #         current_paragraph.append(line)
            #
            # # Добавляем последний абзац, если он есть
            # if current_paragraph:
            #     page_dict['paragraphs'].append(current_paragraph)

            # Конвертация отступов в сантиметры
            for key in page_dict['margins']:
                page_dict['margins'][key] = points_to_cm(page_dict['margins'][key])

            page_data.append(page_dict)
        
        return page_data

def format_paragraphs(paragraphs):
    formatted_paragraphs = []
    for paragraph in paragraphs:
        current_font = None
        current_text = []
        formatted_paragraph = []

        for line in paragraph:
            fontname = line.get('fontname')
            text = line['text']

            if fontname != current_font:
                if current_font is not None:
                    formatted_paragraph.append((current_font, ' '.join(current_text)))
                current_font = fontname
                current_text = [text]
            else:
                current_text.append(text)

        if current_text:
            formatted_paragraph.append((current_font, ' '.join(current_text)))

        formatted_paragraphs.append(formatted_paragraph)

    return formatted_paragraphs

# Пример использования
pdf_path = "path/to/pdf"
page_data = get_margins_and_paragraphs(pdf_path)

# Форматирование результатов
for page in page_data:
    print(f"Page {page['page_num'] + 1}:")
    print(f"  Top Margin: {page['margins']['top']:.2f} cm")
    print(f"  Bottom Margin: {page['margins']['bottom']:.2f} cm")
    print(f"  Left Margin: {page['margins']['left']:.2f} cm")
    print(f"  Right Margin: {page['margins']['right']:.2f} cm")

    print("  Paragraphs:")
    formatted_paragraphs = format_paragraphs(page['paragraphs'])
    for i, formatted_paragraph in enumerate(formatted_paragraphs, 1):
        print(f"    Paragraph {i}:")
        for font, text in formatted_paragraph:
            print(f"      {font} - \"{text}\"")
    print()