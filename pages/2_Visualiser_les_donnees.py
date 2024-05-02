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


# def auth_gspread():
#     scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
#              "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
#     google_service_account_info = st.secrets['google_service_account']
#     creds = ServiceAccountCredentials.from_json_keyfile_dict(
#         google_service_account_info, scope)
#     client = gspread.authorize(creds)
#     return client


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

    st.download_button(
        label='Télécharger emails',
        data=emails.to_csv(index=False, header=False),
    )
    display_sidebar()
    # with st.sidebar:
    #     st.image('./logo.png', width=200)
    #     st.header(":orange[Dernière modification :]")
    #     st.text(meta_data['last_fetched'])

    st.dataframe(df)
    with st.expander("URLs blacklistées"):
        df_blacklist = pd.DataFrame(black_list)
        st.dataframe(df_blacklist)


main()
