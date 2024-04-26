import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
st.set_page_config(layout="wide")

if 'current_database' not in st.session_state:
    st.session_state.current_database = '1yozpUI5mdkpBSCiZoBnENzrVJEfHpisDg0a7ohqQEe4'


def auth_gspread():
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
    google_service_account_info = st.secrets['google_service_account']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        google_service_account_info, scope)
    client = gspread.authorize(creds)
    return client


def get_data():
    client = auth_gspread()
    id = st.session_state['current_database']
    data = client.open_by_key(id).sheet1.get_all_records()
    black_list = client.open(
        "base_de_donnees").get_worksheet(1).get_all_values()
    return data, black_list


def main():
    data, black_list = get_data()

    with st.sidebar:
        st.image('./logo.png', width=200)

    st.title("Base de données")
    df = pd.DataFrame(data)
    st.dataframe(df)

    with st.expander("URLs blacklistées"):
        df_blacklist = pd.DataFrame(black_list)
        st.write(df_blacklist)


main()
