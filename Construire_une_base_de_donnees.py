import streamlit as st
from meta_data_handler import change_current_metadata, get_metadata

from google_search_api import (
    choose_locations_to_search,
    is_in_database,
    is_blacklisted,
    create_queries,
    google_search_simple_query,
    add_to_spreadsheet,
    get_history_of_used_keywords
)


st.set_page_config(layout="wide")


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
    all_meta_data, current_metadata = get_metadata()
    with st.sidebar:
        st.header(':orange[INFORMATIONS]')
        display_selection_bdd(all_meta_data)
        st.subheader(':orange[Dernière mise à jour]')
        st.write(current_metadata['last_fetched'])
        st.subheader(':orange[Recherches passées]')
        for keyword in get_history_of_used_keywords():
            st.text(keyword)
        if 'nbre_emails' in current_metadata.keys():
            st.subheader(':orange[Nbre total emails recensés]')
            st.text(current_metadata['nbre_emails'])


def display_selection_bdd(all_meta_data):
    selected = st.selectbox(
        label='Choisir une autre base de données',
        index=None,
        options=all_meta_data.keys(),
        format_func=lambda id: all_meta_data[id]['file_name']
    )
    if selected is not None and selected != st.session_state.current_metadata['id']:
        change_current_metadata(selected)
        st.rerun()


def display_main_panel():
    _, current_meta_data = get_metadata()
    display_sidebar()
    st.title("Recherches entreprises locations de structures gonflables")

    sheet_name = current_meta_data['file_name']
    st.subheader(f"Création de la base de données : :orange[{sheet_name}]")

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
