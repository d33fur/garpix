import json

'''def load_json(filename):
    json_file = open(filename,encoding="utf8")
    gost = json.load(json_file)
    return gost

CURRENT_STANDARD_JSON = load_json("example.json")
CURRENT_PDF_JSON = load_json("structuredData.json")'''

def check_page_numbering():
    error_message = []
    parametrs = CURRENT_STANDARD_JSON["report_format"]["page_numbering"]
    style = parametrs['style']
    position = parametrs['position']
    starting_page = parametrs['starting_page']
    def generate_numbering(style,starting_page):
        page_count = CURRENT_PDF_JSON['extended_metadata']['page_count']
        match style:
            case 'ARABIC':
                return list(map(str,range(starting_page, page_count + 1)))
            case _:
                return []
    
    def numbering_page_element(position):
        ans = []
        match position[0]:
            case 'Bottom':
                previous_element = None
                for element in CURRENT_PDF_JSON['elements']:
                    if element['Page'] == 0:
                        previous_element = element
                        continue
                    if element['Page'] != previous_element['Page']:
                       ans.append(previous_element)
                    previous_element = element
                ans.append(previous_element)
                return ans  
            case _:
                return []
            
    numbering = generate_numbering(style,starting_page)
    for page_num,element in enumerate(numbering_page_element(position),1):
        if page_num < starting_page:
            continue
        if "Text" in element:
            if element['Text'] != numbering[page_num - starting_page]:
                error_message.append({'error_desc':'Неправильная нумерации страницы. Должно быть ' + '"' + numbering[page_num - starting_page] + '"',
                                  'error_page': element['Page'] + 1,
                                  'error_text': element['Text'] })
            else:
                if "TextAllign" in element['attributes']:
                    if element['attributes']['TextAllign'] != position[1]:
                        error_message.append({'error_desc':'Неправильное расположение по ширине',
                                              'error_page': element['Page'] + 1,
                                              'error_text': element['Text'] })
                else:
                    error_message.append({'error_desc':'Неправильное расположение по ширине',
                                          'error_page': element['Page'] + 1,
                                          'error_text': element['Text'] })
                
        else:
            error_message.append({'error_desc':'Нет нумерации страницы',
                                  'error_page': element['Page'] + 1,
                                  'error_text': None })
    return error_message

'''print(check_page_numbering())'''
