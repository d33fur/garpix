import streamlit as st
import requests
import io
import os
import tempfile
import json
from streamlit_pdf_viewer import pdf_viewer
from docx2pdf import convert


def convert_docx_to_pdf(file_docx):
    with tempfile.NamedTemporaryFile(suffix=".pdf", dir=os.path.dirname(__file__)) as temp_pdf:
        convert(file_docx, temp_pdf.name)
        with open(temp_pdf.name, "rb") as f:
            pdf_bytes = f.read()
    return pdf_bytes 

def on_change_uploaded_file():
    if st.session_state['file'] == None:
        return
    uploaded_file = st.session_state['file']
    binary_data = uploaded_file.getvalue()
    if uploaded_file.type != "application/pdf":
        bytes_io = io.BytesIO(uploaded_file.getvalue())
        with tempfile.NamedTemporaryFile(suffix=".docx", dir=os.path.dirname(__file__)) as f:
            f.write(bytes_io.getvalue())
            binary_data = convert_docx_to_pdf(f.name)
    st.session_state.uploaded_file = binary_data

def get_standards():
    ans = requests.get(url="http://garpix_backend:8000/list").text
    list_standards = []
    for i in ans[1:-1].split(","):
        if i.strip():
            list_standards.append(i.strip()[1:-1])
    return list_standards

def on_change_selectbox():
    headers = {
        "standart": st.session_state.standard
    }
    files = {
        "file": st.session_state.uploaded_file
    }
    response = requests.post(url="http://garpix_backend:8000/check", files=files, headers=headers)
    if response.status_code == 200:
        tmp = json.loads(response.text)
        st.session_state.new_file = tmp["errors"]


def main():
    st.set_page_config(layout="wide", page_icon='📄')
    st.title('Система автоматизированного нормоконтроля')

    with st.sidebar:
        uploaded_file = st.file_uploader("Загрузите документ", type=['docx', 'pdf'], key='file', on_change=on_change_uploaded_file)
        # st.header("Размеры")
        # width = st.slider(label="Ширина", min_value=100, max_value=1000, value=700)
        width = 700
        # height = st.slider(label="Высота", min_value=-1, max_value=1000, value=-1)
        height = -1
        list_standards = get_standards()
        # if uploaded_file is not None:
        st.header("Выберите ГОСТ")
        element = st.selectbox(label = "ГОСТ",options=list_standards, label_visibility="hidden", key="standard", index=None)
        
        if element is not None and uploaded_file is not None:
            st.button("Отправить на проверку", on_click=on_change_selectbox)
    
    if uploaded_file is not None and 'uploaded_file' in st.session_state:
            col1, col2 = st.columns([0.5, 0.5])
            with col1:
                pdf_viewer(input=st.session_state.uploaded_file, width=width, height=height if height != -1 else None, render_text=True)
            with col2:
                if 'new_file' in st.session_state:
                    result = "Документ соответствует ГОСТу" if st.session_state.new_file == "" else "Документ не соответствует ГОСТу"
                    st.subheader(result)
                    st.markdown(st.session_state.new_file)

if __name__ == "__main__":
    main()