import streamlit as st
from datetime import datetime
from google_drive_api import (
    button_to_create_spread_sheet,
    open_file,
    delete_file,
    get_files_infos_in_drive
)

from streamlit_modal import Modal


def main_panel_results(items):

    for item in items:
        col1, col2 = st.columns([7, 4])
        with col1:
            st.write('Nom de la base de données : ', item['name'])
            last_modified = datetime.strptime(
                item['modifiedTime'], "%Y-%m-%dT%H:%M:%S.%fZ")
            last_modified = last_modified.replace(microsecond=0, tzinfo=None)

            st.write("Dernière mise à jour : ", last_modified)
        with col2:
            sub_col1, sub_col2 = st.columns([2, 3])
            with sub_col1:
                if st.button('Ouvrir', key=f"open_{item['id']}"):
                    open_file(item['id'])
            with sub_col2:
                asked_for_delete = st.toggle(
                    label='Supprimer',
                    value=False,
                    key=f"open_delete_{item['id']}")

        if asked_for_delete:
            st.error('La suppression est définitive', icon='☠️')
            if st.button('Supprimer', key=f"delete_{item['id']}"):
                delete_file(item['id'])
        st.divider()


button_to_create_spread_sheet()
results = get_files_infos_in_drive()
items = results.get('files', [])
main_panel_results(items)
