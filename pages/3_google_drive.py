import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.http import MediaFileUpload
import io
from googleapiclient.errors import HttpError
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st
from datetime import datetime
from streamlit_extras.switch_page_button import switch_page


def auth_drive():
    scope = ['https://www.googleapis.com/auth/drive']
    google_service_account_info = st.secrets['google_service_account']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        google_service_account_info, scope)

    service = build('drive', 'v3', credentials=creds)
    return service


def button_to_create_spread_sheet():
    if st.button('Create New Spreadsheet'):
        file_metadata = {
            'name': 'Again again ?',
            'mimeType': 'application/vnd.google-apps.spreadsheet',
            'parents': '1yyTtlqhg41kd7NN7QBAtRUcih4XHV5FD',
        }
        shared_permissions = {
            'role': 'writer',
            'type': 'user',
            'emailAddress': 'florian.dadouchi@gmail.com'
        }
        try:
            service = get_drive_service()
            file = service.files().create(
                body=file_metadata, fields='id').execute()

            permission = service.permissions().create(
                fileId=file.get('id'),
                body=shared_permissions
            ).execute()

            st.success(f"New spreadsheet created with ID: {file.get('id')}")
        except HttpError as error:
            st.error(f"An error occurred: {error}")
            file = None


@st.cache_data
def get_drive_service():
    service = auth_drive()
    return service


@st.cache_data
def get_files_infos_in_drive():
    service = get_drive_service()
    results = service.files().list(pageSize=1000,
                                   fields="nextPageToken, files(id, name, mimeType, size, modifiedTime)").execute()
    return results


def open_file(item_id):
    st.session_state['current_database'] = item_id
    st.write(f"Opening file with ID: {st.session_state['current_database']}")
    switch_page('base de donnees')


def main_panel_results(items):
    for item in items:
        col1, col2 = st.columns([7, 3])
        with col1:
            st.write('Nom de la base de données : ', item['name'])
            last_modified = datetime.strptime(
                item['modifiedTime'], "%Y-%m-%dT%H:%M:%S.%fZ")
            last_modified = last_modified.replace(microsecond=0, tzinfo=None)

            st.write("Dernière mise à jour : ", last_modified)
        with col2:
            sub_col1, sub_col2 = st.columns(2)
            with sub_col1:
                if st.button('Ouvrir', key=f"open_{item['id']}"):
                    open_file(item['id'])
            with sub_col2:
                st.button('Supprimer', f"delete_{item['id']}")
        st.divider()


results = get_files_infos_in_drive()
items = results.get('files', [])
main_panel_results(items)
