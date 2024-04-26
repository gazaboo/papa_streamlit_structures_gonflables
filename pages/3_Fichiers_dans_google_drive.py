import streamlit as st
from datetime import datetime
from google_drive_api import (
    button_to_create_spread_sheet,
    open_file,
    delete_file,
    get_files_infos_in_drive
)
from meta_data_handler import get_metadata


def main_panel_results():
    st.title('Bases de données existantes')

    with st.sidebar:
        button_to_create_spread_sheet()

    all_metadata, _ = get_metadata()
    for item in all_metadata.values():
        col1, col2 = st.columns([7, 4])
        with col1:
            st.subheader(f":orange[{item['file_name']}]")
            last_modified = item['last_fetched'].replace(
                microsecond=0, tzinfo=None)

            st.write("Dernière mise à jour : ", last_modified)
            st.link_button(
                label='Ouvrir dans google drive',
                url='https://docs.google.com/spreadsheets/d/' + item['id'])
        with col2:
            sub_col1, sub_col2 = st.columns([2, 3])
            with sub_col1:
                if st.button("Visualiser", key=f"open_{item['id']}"):
                    open_file(item['id'])
            with sub_col2:
                asked_for_delete = st.toggle(
                    label=':red[Supprimer]',
                    value=False,
                    key=f"open_delete_{item['id']}")

        if asked_for_delete:
            st.error('La suppression est définitive', icon='☠️')
            if st.button('Supprimer', key=f"delete_{item['id']}"):
                delete_file(item['id'])
        st.divider()


main_panel_results()
