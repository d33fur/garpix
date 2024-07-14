import json

'''def load_json(filename):
    json_file = open(filename,encoding="utf8")
    gost = json.load(json_file)
    return gost

CURRENT_STANDARD_JSON = load_json("example.json")
CURRENT_PDF_JSON = load_json("structuredData.json")'''

section_titles = [
    "СПИСОК ИСПОЛНИТЕЛЕЙ",
    "РЕФЕРАТ",
    "СОДЕРЖАНИЕ",
    "ТЕРМИНЫ И ОПРЕДЕЛЕНИЯ",
    "ПЕРЕЧЕНЬ СОКРАЩЕНИЙ И ОБОЗНАЧЕНИЙ",
    "ВВЕДЕНИЕ",
    "ЗАКЛЮЧЕНИЕ",
    "СПИСОК ИСПОЛЬЗОВАННЫХ ИСТОЧНИКОВ",
    "ПРИЛОЖЕНИЕ"
    ]

def check_font():  
    error_message = []
    parametrs = CURRENT_STANDARD_JSON["report_format"]["font"]
    color = parametrs['color']
    min_size = int(parametrs['min_size'])
    fontname = parametrs['default_type']
    bold_text_types = parametrs['bold']
    italic_text_types = parametrs['italic']

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
        for element in CURRENT_PDF_JSON['elements']:
            if is_text(element):
                if element['TextSize'] < (min_size - epsilon):
                    if current_page != element['Page']:
                        error_message.append({'error_desc':'Размер шрифта меньше необходимых ' + str(min_size) + 'pt',
                                              'error_page': element['Page'] + 1,
                                              'error_text': element['Text'] })
                current_page = element['Page']
        return error_message

    def check_font_type(fontname):
        error_message = []
        heauristic_ratio = 0.9
        text_length = 0.0
        conventional_text_length = 0.0
        for element in CURRENT_PDF_JSON['elements']:
            if is_text(element):
                text_length += len(element['Text'])
                if is_correct_font(element,fontname):
                    conventional_text_length += len(element['Text'])
        if (conventional_text_length / text_length) < heauristic_ratio:
            error_message.append({'error_desc':'Использованный в документе шрифт не соответствует ' + str(fontname),
                                  'error_page': None,
                                  'error_text': element['Text']})
        return error_message

    def check_bold(bold_text_types):
        error_message = []
        for category in bold_text_types:
            if category == 'section_titles':
                for element in CURRENT_PDF_JSON['elements']:
                    if is_text(element):
                        if element['Text'] in section_titles and not is_bold(element):
                            error_message.append({'error_desc':'Заголовок структурного элемента \'' + category + '\' не выделен полужирном шрифтом',
                                                  'error_page': element['Page'] + 1,
                                                  'error_text': element['Text']})
        return error_message

    def check_italic(italic_text_types):
        error_message = []
        for category in italic_text_types:
            if category == 'terms_in_latin':
                for element in CURRENT_PDF_JSON['elements']:
                    if is_text(element) and "Lang" in element:
                        if (element['Lang'] == 'ru') and is_italic(element):
                            error_message.append({'error_desc':'Текст не должен быть выделен курсивом',
                                                  'error_page': element['Page'] + 1,
                                                  'error_text': element['Text']})
        return error_message
 
    error_message = (check_color(color)+
           check_font_size(min_size)+
           check_font_type(fontname)+
           check_bold(bold_text_types)+
           check_italic(italic_text_types))
    return error_message


'''error = check_font()
print(type(error[0]))
print(error)'''
