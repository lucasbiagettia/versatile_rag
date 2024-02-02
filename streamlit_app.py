import os
import streamlit as st
from aap3 import AppManager
from inference_model.answer_generator import InferenceModel
from vectorizer import EmbeddingModel
 

if "app_manager" not in st.session_state:
    st.session_state.app_manager = AppManager()

if "db_name" not in st.session_state:
    st.session_state.db_name = 'vectorpoc'

if "embedding_model" not in st.session_state:
    st.session_state.embedding_model = EmbeddingModel()

if "selected_document" not in st.session_state:
    st.session_state.selected_document = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "selected_model" not in st.session_state:
    st.session_state.selected_model = "tiiuae/falcon-7b"

if "inference_model" not in st.session_state:
    st.session_state.inference_model = None


def reset_values():
    st.session_state.messages = []


def handle_chat_input(prompt):
    with st.chat_message("user"):
        st.markdown(prompt)
    if st.session_state.inference_model is None:
        st.session_state.inference_model = InferenceModel(st.session_state.selected_model)
    with st.chat_message("assistant"):
        db_name = st.session_state.db_name
        document = st.session_state.selected_document
        question = prompt
        embedding_model = st.session_state.embedding_model
        inference_model = st.session_state.inference_model
        app_manager = st.session_state.app_manager
        response = app_manager.make_question(db_name, document, question, embedding_model, inference_model)
        st.markdown(str(response))

def add_document(uploaded_file):
    app_manager = st.session_state.app_manager
    db_name = st.session_state.db_name
    app_manager.add_document(db_name, uploaded_file, st.session_state.embedding_model)

def get_avaible_documents():
    app_manager = st.session_state.app_manager
    db_name = st.session_state.db_name
    return app_manager.get_all_tables(db_name)

def print_all_messages(messages):
    for message in messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

def main():
    st.header("Vas a preguntar")

    with st.sidebar:
        if st.sidebar.button("Reiniciar"):
            reset_values()

        options = get_avaible_documents()

        selected_option = st.selectbox('Select an option:', options)
        st.write('You have selected:', selected_option)
        if selected_option is not None:
            st.session_state.selected_document = selected_option

        selected_model = st.text_input("Select a model", value="tiiuae/falcon-7b")
        st.session_state.selected_model = selected_model
        st.write('Modelo seleccionado', selected_model)

        embedding_models = ['PlanTL-GOB-ES/roberta-base-bne']
        embedding_model = st.selectbox('Select an option:', embedding_models)
        st.write('You have selected:', embedding_model)
        if selected_option is not None:
            st.session_state.embedding_model = EmbeddingModel()

        uploaded_file = st.file_uploader('Select a file', type=['pdf'])
        file_name2 = st.text_input("Ingresa el nombre del archivo:")
        if st.button("Upload File"):
            if uploaded_file is not None and file_name2:
                app_manager = st.session_state.app_manager
                db_name = st.session_state.db_name
                app_manager.add_document(db_name, uploaded_file, st.session_state.embedding_model)
                file_name, file_extension = os.path.splitext(uploaded_file.name)
                st.write(f'You have uploaded the file: {file_name}')
            else:
                st.write('Debes seleccionar un archivo y asignarle nombre')


    print_all_messages(st.session_state.messages)

    prompt = st.chat_input("Ayúdame a continuar escribiendo")
    if prompt:
        handle_chat_input(prompt)


if __name__ == "__main__":
    main()