import streamlit as st
from google_drive_api import get_files_infos_in_drive


def get_metadata():
    if 'meta_data_drive_files' not in st.session_state:
        get_files_infos_in_drive.clear()
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
