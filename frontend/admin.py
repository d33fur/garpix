import streamlit as st
import requests
import json

BASE_URL = "http://garpix_backend:8000"

def get_all_standards():
    response = requests.get(f"{BASE_URL}/get_all")
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Ошибка при получении данных.")
        return []

def add_standard(name, json_data):
    data = {"standard_name": name, "standard_json": json_data}
    response = requests.post(f"{BASE_URL}/add", json=data)
    if response.status_code == 200:
        st.success("ГОСТ успешно добавлен или обновлен.")
    else:
        st.error("Ошибка при добавлении ГОСТа.")

def delete_standard(name):
    data = {"standard_name": name}
    response = requests.post(f"{BASE_URL}/delete", json=data)
    if response.status_code == 200:
        st.success("ГОСТ успешно удален.")
    else:
        st.error("Ошибка при удалении ГОСТа.")

def main():
    st.sidebar.title("Админ Панель")
    option = st.sidebar.selectbox("Выберите действие", ("Показать все данные", "Добавить", "Удалить"))

    if option == "Показать все данные":
        st.header("Все данные")
        standards = get_all_standards()
        for standard in standards:
            st.subheader(standard['standard_name'])
            st.json(standard['standard_json'])

    elif option == "Добавить":
        st.header("Добавить ГОСТ")
        name = st.text_input("Название ГОСТа")
        json_data = st.text_area("JSON данные ГОСТа")
        if st.button("Добавить"):
            if name and json_data:
                try:
                    json_data = json.loads(json_data)
                    add_standard(name, json_data)
                except ValueError:
                    st.error("Неверный формат JSON.")
            else:
                st.error("Пожалуйста, заполните все поля.")

    elif option == "Удалить":
        st.header("Удалить ГОСТ")
        name = st.text_input("Название ГОСТа")
        if st.button("Удалить"):
            if name:
                delete_standard(name)
            else:
                st.error("Пожалуйста, введите название ГОСТа.")

if __name__ == "__main__":
    main()
