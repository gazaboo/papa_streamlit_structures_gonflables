import streamlit as st
from authenticators import auth_drive
from datetime import datetime


def get_metadata():
    if 'meta_data_drive_files' not in st.session_state:
        get_files_infos_in_drive()

    if 'current_metadata' not in st.session_state:
        st.session_state.current_metadata = st.session_state.meta_data_drive_files[
            '1yozpUI5mdkpBSCiZoBnENzrVJEfHpisDg0a7ohqQEe4']
        st.session_state.current_metadata['id'] = '1yozpUI5mdkpBSCiZoBnENzrVJEfHpisDg0a7ohqQEe4'
    return st.session_state.meta_data_drive_files, st.session_state.current_metadata


def change_current_metadata(id=None):
    st.write('change_current_metadata')
    if id is not None:
        all_meta_data = st.session_state.meta_data_drive_files
        st.session_state.current_metadata = all_meta_data[id]


def get_files_infos_in_drive():
    service = auth_drive()
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
