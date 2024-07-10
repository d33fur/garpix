import streamlit as st
import requests
import io
import os
import tempfile
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

def get_standards() -> list[str]:
    ans = requests.get(url="http://127.0.0.1:8000/list").text[1:-1]
    list_standards = list()
    for i in ans.split(","):
        list_standards.append(i.strip()[1:-1])
    return list_standards

def on_change_selectbox():
    # if  st.session_state.uploaded_file is None:
    #     return
    headers = {
        "standart": st.session_state.standard
    }
    files = {
        "file": st.session_state.uploaded_file
    }
    response = requests.post(url="http://127.0.0.1:8000/check", files=files, headers=headers)
    print(response.status_code)


def main():
    st.title('Система автоматизированного нормоконтроля')

    with st.sidebar:
        uploaded_file = st.file_uploader("Загрузите документ", type=['docx', 'pdf'], key='file', on_change=on_change_uploaded_file)
        st.header("Размеры")
        width = st.slider(label="Ширина", min_value=100, max_value=1000, value=700)
        height = st.slider(label="Высота", min_value=-1, max_value=1000, value=-1)
        list_standards = get_standards()
        if "uploaded_file" in st.session_state:
            st.header("Выберите ГОСТ")
            st.selectbox(label = "ГОСТ",options=list_standards, label_visibility="hidden", on_change=on_change_selectbox, key="standard", index=None)
    
    tab1, tab2 = st.tabs(["Оригинал", "Исправленный"])
    with tab1:
        if uploaded_file is not None and 'uploaded_file' in st.session_state:
            pdf_viewer(input=st.session_state.uploaded_file, width=width, height=height if height != -1 else None)

    with tab2:
        ## add new file from backend
        pass

if __name__ == "__main__":
    main()