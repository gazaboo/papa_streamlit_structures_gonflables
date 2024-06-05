from google_drive_api import button_to_create_spread_sheet
from google_search_api import get_history_of_used_keywords
from meta_data_handler import change_current_metadata, get_metadata
import streamlit as st


def display_sidebar():
    all_meta_data, current_metadata = get_metadata()
    with st.sidebar:
        st.header(':orange[INFORMATIONS]')
        display_selection_bdd(all_meta_data)
        button_to_create_spread_sheet()
        st.subheader(':orange[Dernière mise à jour]')
        st.write(current_metadata['last_fetched'])
        st.subheader(':orange[Recherches passées]')
        history_keywords = get_history_of_used_keywords()
        for keyword in history_keywords:
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
        st.cache_data.clear()
        st.rerun()
