import json

def load_json(filename):
    json_file = open(filename,encoding="utf8")
    gost = json.load(json_file)
    return gost

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


def check_color(document, color):
    error_message = ''
    return error_message

def check_font_size(document,min_size):
    error_message = ''
    current_page = -1
    epsilon = 0.1
    for element in document['elements']:
        if is_text(element):
            if element['TextSize'] < (min_size - epsilon):
                if current_page != element['Page']:
                    error_message += 'On page ' + str(element['Page'] + 1) + ' font size is less than given ' + str(min_size) + ' pt' + '\n'
                current_page = element['Page']
    return error_message

def check_font_type(document, fontname):
    error_message = ''
    heauristic_ratio = 0.9
    text_length = 0.0
    conventional_text_length = 0.0
    for element in document['elements']:
        if is_text(element):
            text_length += len(element['Text'])
            if is_correct_font(element,fontname):
                conventional_text_length += len(element['Text'])
    print(conventional_text_length / text_length)
    if (conventional_text_length / text_length) < heauristic_ratio:
        error_message = 'Overall wrong font type used' + '\n'
    return error_message

def check_bold(document, bold_text_types):
    error_message = ''
    for category in bold_text_types:
        if category == 'section_titles':
            for element in document['elements']:
                if is_text(element):
                    if element['Text'] in section_titles and not is_bold(element):
                        error_message += 'Section header ' + element['Text'] + ' is not bold' + '\n'  
    return error_message

def check_italic(document, italic_text_types):
    error_message = ''
    for category in italic_text_types:
        if category == 'terms_in_latin':
            for element in document['elements']:
                if is_text(element) and "Lang" in element:
                    if element['Lang'] == 'ru' and is_italic(element):
                        error_message += 'On page ' + str(element['Page'] + 1) + ' ' + element['Text'] + ' cant be italic' + '\n'
    return error_message


def check_font(GOST, document):
    parametrs = GOST["report_format"]["font"]
    color = parametrs['color']
    min_size = int(parametrs['min_size'])
    fontname = parametrs['default_type']
    bold_text_types = parametrs['bold']
    italic_text_types = parametrs['italic']
    error_message = (check_color(document,color)+
           check_font_size(document,min_size)+
           check_font_type(document,fontname)+
           check_bold(document,bold_text_types)+
           check_italic(document,italic_text_types))
    return error_message


'''print(check_font(load_json("example.json"),load_json("structuredData.json")))'''
