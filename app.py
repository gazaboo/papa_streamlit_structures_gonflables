import streamlit as st
from google_search_api import (
    choose_locations_to_search,
    is_in_database,
    is_blacklisted,
    create_queries,
    google_search_simple_query,
    add_to_spreadsheet,
    get_history_of_used_keywords
)

from google_drive_api import get_files_infos_in_drive

st.set_page_config(layout="wide")

if 'meta_data_drive_files' not in st.session_state:
    get_files_infos_in_drive.clear()
    get_files_infos_in_drive()

if 'current_metadata' not in st.session_state:
    st.session_state.current_metadata = st.session_state.meta_data_drive_files[
        '1yozpUI5mdkpBSCiZoBnENzrVJEfHpisDg0a7ohqQEe4']
    st.session_state.current_metadata['id'] = '1yozpUI5mdkpBSCiZoBnENzrVJEfHpisDg0a7ohqQEe4'


def display_site_info(item):
    st.subheader(item.get('title'))
    if is_in_database(item):
        st.warning('Deja dans la base de données')
    if is_blacklisted(item):
        st.error('Dans la liste noire, ne sera pas ajoutée dans la base de données')
    st.write(item.get('snippet'))
    st.write(item.get('link'))
    st.divider()


def display_sidebar():
    with st.sidebar:
        st.image('./logo.png', width=150)
        st.header('INFORMATIONS')
        st.divider()
        st.subheader('Dernière mise à jour')
        st.write(st.session_state.current_metadata['last_fetched'])
        st.divider()
        st.subheader('Recherches passées')
        for keyword in get_history_of_used_keywords():
            st.text(keyword)
        st.divider()
        st.subheader('Nbre total emails recensés')
        st.text(st.session_state.current_metadata['nbre_emails'])


def display_selection_bdd():
    options = st.session_state.meta_data_drive_files
    selected_id = st.selectbox(
        label='Choisir base de données',
        options=options.keys(),
        format_func=lambda id: options[id]['file_name']
    )
    return selected_id


def display_main_panel():
    st.title("Recherches entreprises locations de structures gonflables")
    st.subheader("Création de la base de données")
    st.session_state.current_database = display_selection_bdd()
    st.write(
        st.session_state.meta_data_drive_files[st.session_state.current_database])
    display_sidebar()
    user_query = st.text_input("Recherche google")
    locations = choose_locations_to_search()
    if st.button("Search") and user_query:
        compound_queries = create_queries(user_query, locations)
        total_elements = len(compound_queries*10)
        progress_bar = st.progress(1/total_elements, text='Searching')
        index = 1
        for compound_query in compound_queries:
            query, countryCode, countryName, city = compound_query
            st.subheader(" - ".join([query,  city, countryName]))
            with st.expander("Resultats"):
                results = google_search_simple_query(
                    countryCode=countryCode, query=query + " " + city).get("items", [])
                for item in results:
                    progress_bar.progress(
                        index/total_elements, text=f'Recherche : {index} / {total_elements} ({city} - {countryName})')
                    display_site_info(item)
                    add_to_spreadsheet(item, countryName, city, query)
                    index += 1


display_main_panel()
