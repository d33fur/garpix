def title_text_accordance():
    import json
    import requests
    import uuid
    import os
    from dotenv import load_dotenv

    def get_env():
        file = "auth.env"
        if os.path.exists(file):
            load_dotenv(file)

    get_env()

    def get_access_token():
        request_id = uuid.uuid4()
        url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
        payload='scope=GIGACHAT_API_PERS'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'RqUID': request_id.__str__(),
            'Authorization': f'Basic {os.environ.get('GIGACHAT_AUTH')}'
        }
        response = requests.request("POST", url, headers=headers, data=payload, verify=False)
        return response.json()['access_token']

    access_token = get_access_token()

    def get_all_text():
        elements = CURRENT_PDF_JSON['elements']
        headers = []
        element_pos = 0
        for element in elements:
            if '//Document/H1' in element['Path']:
                headers.append({
                    'title': element['Text'],
                    'header_pos': element_pos,
                    'next_header_pos': -1,
                    'text': '',
                })
            element_pos += 1
        if len(headers) == 0:
            return None
        for i in range(len(headers)-1):
            headers[i]['next_header_pos'] = headers[i+1]['header_pos']
        element_pos = 0
        cur_header = 0
        for element in elements:
            if element_pos > headers[cur_header]['header_pos']:
                if element_pos < headers[cur_header]['next_header_pos'] or headers[cur_header]['next_header_pos'] == -1:
                    if 'Text' in element:
                        headers[cur_header]['text'] += element['Text']
                else:
                    cur_header = cur_header + 1
                    if cur_header >= len(headers):
                        break
            element_pos += 1
        return headers

    def send_evaluation_request(title, text):
        url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
        payload = json.dumps({
            "model": "GigaChat",
            "messages": [
                {
                    "role": "user",
                    "content": f"Оцени от 0 до 100, насколько текст подходит заголовку. Выведи цифру. Заголовок: {title}. Текст: {text}"
                }
            ],
            "stream": False,
            "repetition_penalty": 1
        })
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
        response = requests.request("POST", url, headers=headers, data=payload, verify=False)
        return response.json()["choices"][0]["message"]["content"]

    hds = get_all_text()
    found_errors = []
    errors_desc = CURRENT_ERRORS_JSON['errors']
    for header in hds:
        eval = send_evaluation_request(header['title'], header['text'])
        if eval.isdigit():
            if int(eval) < 50:
                found_errors.append(errors_desc[8]['description'] + f'\n- заголовок {header['title']}')
    return found_errors
