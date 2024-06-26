import streamlit as st
from datetime import datetime
from streamlit_extras.switch_page_button import switch_page
from google_search_api import auth_gspread
from authenticators import auth_drive
from googleapiclient.errors import HttpError


def button_to_create_spread_sheet():
    st.header(':orange[Nouvelle recherche]')
    spread_sheet_name = st.text_input(
        label='Nouvelle recherche',
        label_visibility='collapsed',
        placeholder='Nom de la base de données...'
    )
    if st.button('Créer') and len(spread_sheet_name) > 0:
        file_metadata = {
            'name': spread_sheet_name,
            'mimeType': 'application/vnd.google-apps.spreadsheet',
            'parents': '1yyTtlqhg41kd7NN7QBAtRUcih4XHV5FD',
        }
        shared_permissions = {
            'role': 'writer',
            'type': 'user',
            'emailAddress': 'florian.dadouchi@gmail.com'
        }

        shared_permissions_papa = {
            'role': 'writer',
            'type': 'user',
            'emailAddress': 'najib.dadouchi@gmail.com'
        }

        try:
            drive_client = get_drive_service()
            gspread_client = auth_gspread()

            file_id = drive_client.files().create(
                body=file_metadata, fields='id').execute().get('id')

            permission = drive_client.permissions().create(
                fileId=file_id,
                body=shared_permissions
            ).execute()

            permission = drive_client.permissions().create(
                fileId=file_id,
                body=shared_permissions_papa
            ).execute()

            sheet = gspread_client.open_by_key(file_id).sheet1
            sheet.append_row([
                'Titre', 'Description', 'URL', 'Email', 'Pays', 'Ville', 'Mots clés'
            ])

            new_metadata = {
                'id': file_id,
                'file_name': spread_sheet_name,
                'last_fetched': datetime.now(),
                'last_modified': datetime.now(),
                'mots_cles': set(),
                'nbre_emails': 0
            }
            st.session_state['meta_data_drive_files'][file_id] = new_metadata
            st.session_state.current_metadata = new_metadata
            switch_page('Construire une base de donnees')

        except HttpError as error:
            st.error(f"An error occurred: {error}")
            file_id = None
    st.divider()


def get_drive_service():
    service = auth_drive()
    return service


@st.cache_data(ttl=5)
def get_files_infos_in_drive():
    service = get_drive_service()
    results = service.files().list(pageSize=1000,
                                   fields="nextPageToken, files(id, name, mimeType, size, modifiedTime)").execute()

    if 'meta_data_drive_files' not in st.session_state:
        st.session_state['meta_data_drive_files'] = {}

    for result in results['files']:
        keys = st.session_state['meta_data_drive_files'].keys()
        if result['id'] not in keys:
            st.session_state['meta_data_drive_files'][result['id']] = {
                'id': result['id'],
                'file_name': result['name'],
                'last_modified': result['modifiedTime'],
                'last_fetched': datetime.now()
            }
        else:
            elt = st.session_state['meta_data_drive_files'][result['id']]
            elt['file_name'] = result['name']
            elt['last_modified'] = result['modifiedTime'],
            elt['last_fetched'] = datetime.now()

    return results


def open_file(id):
    st.session_state.current_metadata = st.session_state.meta_data_drive_files[id]
    switch_page('Visualiser les donnees')


def delete_file(id):
    client = auth_gspread()
    id_to_delete = st.session_state.meta_data_drive_files[id]['id']
    client.del_spreadsheet(id_to_delete)
    get_files_infos_in_drive.clear()
