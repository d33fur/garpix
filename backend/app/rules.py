import re

def all_check(CURRENT_PDF_JSON, CURRENT_STANDARD_JSON):
    result = ""
    def images_check():
        standard = dict()

        def parse_standard_json():
            standard['FontSize'] = re.findall(string=CURRENT_STANDARD_JSON['report_format']['font']['size'], pattern=r'(\d+)')[0]
            standard['FontType'] = ''.join(CURRENT_STANDARD_JSON['report_format']['font']['type'].split()) + "PSMT"
            standard['title_position'] = CURRENT_STANDARD_JSON['report_format']['illustrations']['title_position'].capitalize()
            standard['word'] = CURRENT_STANDARD_JSON['report_format']['illustrations']['reference_in_text']['word'].capitalize()

        parse_standard_json()

        elements = CURRENT_PDF_JSON['elements']
        pattern = re.compile(r'//Document/Figure(?:\[(\d+)\])?')

        # //Document/Figure(?:\[(\d+)\])?
        errors_list = list()

        for i in range(len(elements)):
            part = elements[i]
            match = pattern.search(part['Path'])
            if match and 'Text' not in part:
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
                    next_match = next_pattern.search(next_part['Text'])

                if next_match and before_match:
                    # Проверка шрифтов и положения
                    next_part_align = next_part['attributes']['TextAlign']
                    next_part_font = next_part['Font']['name']
                    next_part_text_size = next_part['TextSize']

                    before_part_align = before_part['attributes']['TextAlign']
                    before_part_font = before_part['Font']['name']
                    before_part_text_size = before_part['TextSize']

                    if not (next_part_align == standard['title_position'] and standard['FontType'] in next_part_font and next_part_text_size == standard['FontSize']):
                        tmp = f"Проблема с шрифтом или позиционированием текста после изображением. Страница {next_part['Page']}"
                        errors_list.append(tmp)
                    if not (before_part_align == "Justify" and standard['FontType'] in before_part_font and before_part_text_size == standard['FontSize']):
                        tmp = f"Проблема с шрифтом или позиционированием текста перед изображением. Страница {before_part['Page']}"
                        errors_list.append(tmp)
                else: 
                    tmp = f"Проблема с ссылкой или описанием изображения. Страница {part['Page']+1}."
                    if not next_match:
                        tmp = tmp + f"\nТекст из документа: {next_part['Text']}"
                    if not before_match:
                        tmp = tmp + f"\nТекст из документа: {before_part['Text']}"
                    errors_list.append(tmp)

        result_string = '\n'.join(errors_list)
        return result_string
    
    result += images_check()
    return result