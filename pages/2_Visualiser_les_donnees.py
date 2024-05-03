import streamlit as st
import gspread
from authenticators import auth_gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import datetime

from google_drive_api import get_files_infos_in_drive
from meta_data_handler import get_metadata
from sidebar_components import display_sidebar


st.set_page_config(layout="wide")

if 'meta_data_drive_files' not in st.session_state:
    get_files_infos_in_drive.clear()
    get_files_infos_in_drive()

if 'current_metadata' not in st.session_state:
    st.session_state.current_metadata = st.session_state.meta_data_drive_files[
        '1yozpUI5mdkpBSCiZoBnENzrVJEfHpisDg0a7ohqQEe4']
    st.session_state.current_metadata['id'] = '1yozpUI5mdkpBSCiZoBnENzrVJEfHpisDg0a7ohqQEe4'


def get_data():
    client = auth_gspread()
    _, current_metadata = get_metadata()
    id = current_metadata['id']
    sheet = client.open_by_key(id)
    data = sheet.get_worksheet(0).get_all_records()
    if len(sheet.worksheets()) > 1:
        black_list = sheet.get_worksheet(1).get_all_values()
    else:
        black_list = []
    update_meta_data(id, data)
    return data, black_list, st.session_state['meta_data_drive_files'][id]


def update_meta_data(id, data):
    elt = st.session_state['meta_data_drive_files'][id]
    if len(data) > 0:
        df = pd.DataFrame(data)
        elt['last_fetched'] = datetime.now()
        elt['mots_cles'] = df["Mots clés"].unique()
        elt['nbre_emails'] = df["Email"].nunique()
    else:
        elt['last_fetched'] = datetime.now()
        elt['mots_cles'] = ""
        elt['nbre_emails'] = 0


def synchronize_with_remote():
    get_data.clear()
    st.rerun()


def main():
    """
    A function that generates a webpage displaying a database with a title and subheader.
    It creates a download button for subsets of 300 emails, each labeled with the range of emails it contains.
    When clicked, the button downloads the subset as a CSV file without the index and header.
    """
    data, black_list, meta_data = get_data()
    df = pd.DataFrame(data)

    st.title("Base de données")
    st.subheader(f"Nom : :orange{[meta_data['file_name']]}")

    emails = (
        df['Email']
        .dropna()
        .drop_duplicates()
        .str.lower()
        .sort_values()
        .reset_index(drop=True)
        .iloc[1:]
    )

    create_download_buttons(emails)
    display_sidebar()
    st.dataframe(df)
    with st.expander("URLs blacklistées"):
        df_blacklist = pd.DataFrame(black_list)
        st.dataframe(df_blacklist)


def create_download_buttons(emails):
    """
    A function that creates a download button for each subset of 300 emails.
    The button is labeled with the range of emails it contains.
    When clicked, the button downloads the subset of emails as a CSV file
    without the index and header.
    """
    for i in range(0, len(emails), 300):
        end = min(i + 300, len(emails))
        sub_emails = emails[i:end]
        st.download_button(
            label=f'Télécharger les emails numéros {i} à {end} ',
            data=sub_emails.to_csv(index=False, header=False),
        )


main()
