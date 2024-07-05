import streamlit as st
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

def main():
    st.title('Система автоматизированного нормоконтроля')

    with st.sidebar:
        uploaded_file = st.file_uploader("Загрузите документ", type=['docx', 'pdf'])
        st.header("Размеры")
        width = st.slider(label="Ширина", min_value=100, max_value=1000, value=700)
        height = st.slider(label="Высота", min_value=-1, max_value=1000, value=-1)

    if uploaded_file is not None:
        binary_data = uploaded_file.getvalue()
        if uploaded_file.type != "application/pdf":
            bytes_io = io.BytesIO(uploaded_file.getvalue())
            with tempfile.NamedTemporaryFile(suffix=".docx", dir=os.path.dirname(__file__)) as f:
                f.write(bytes_io.getvalue())
                binary_data = convert_docx_to_pdf(f.name)
        st.text(f"ТЕЛО: {binary_data}")        
        pdf_viewer(input=binary_data, width=width, height=height if height != -1 else None)

if __name__ == "__main__":
    main()