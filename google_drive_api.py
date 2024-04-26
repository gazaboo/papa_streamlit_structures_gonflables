from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st
from datetime import datetime
from streamlit_extras.switch_page_button import switch_page

from google_search_api import auth_gspread


def auth_drive():
    scope = ['https://www.googleapis.com/auth/drive']
    google_service_account_info = st.secrets['google_service_account']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        google_service_account_info, scope)

    service = build('drive', 'v3', credentials=creds)
    return service


def button_to_create_spread_sheet():
    col1, col2, col3 = st.columns([3, 3, 2])
    with col1:
        spread_sheet_name = st.text_input(
            label='Nouvelle recherche',
            label_visibility='collapsed',
            placeholder='Nom de la base de données...'
        )
    with col2:
        if st.button('Nouvelle recherche') and len(spread_sheet_name) > 0:
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
            try:
                drive_client = get_drive_service()
                gspread_client = auth_gspread()

                file_id = drive_client.files().create(
                    body=file_metadata, fields='id').execute().get('id')

                permission = drive_client.permissions().create(
                    fileId=file_id,
                    body=shared_permissions
                ).execute()

                sheet = gspread_client.open_by_key(file_id).sheet1
                sheet.append_row([
                    'Titre', 'Description', 'URL', 'Email', 'Pays', 'Ville', 'Mots clés'
                ])

                st.session_state['meta_data_drive_files'][file_id] = {
                    'id': file_id,
                    'file_name': spread_sheet_name,
                    'last_fetched': datetime.now(),
                    'mots_cles': {},
                    'nbre_emails': 0
                }

                st.success(f"New spreadsheet created with ID: {file_id}")
            except HttpError as error:
                st.error(f"An error occurred: {error}")
                file_id = None
    st.divider()


def get_drive_service():
    service = auth_drive()
    return service


@ st.cache_data(ttl=30)
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
    switch_page('base de donnees')


def delete_file(id):
    client = auth_gspread()
    id_to_delete = st.session_state.meta_data_drive_files[id]['id']
    client.del_spreadsheet(id_to_delete)
    get_files_infos_in_drive.clear()
