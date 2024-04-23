import streamlit as st
import requests

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import pandas as pd
st.set_page_config(layout="wide")

# Function to authenticate and create a client.
def auth_gspread():
    scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
    google_service_account_info = st.secrets['google_service_account']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(google_service_account_info, scope)
    client = gspread.authorize(creds)
    return client


# Streamlit user interface
def main():
    client = auth_gspread()
    st.session_state['sheet'] = client.open("base_de_donnees").sheet1
    black_list = client.open("base_de_donnees").get_worksheet(1).get_all_values()
    st.session_state['black_list'] = set([ elt[0] for elt in black_list[1:]])
    st.session_state['data'] = st.session_state.sheet.get_all_records()    
    st.session_state['already_listed_url'] = set([item['Link'] for item in st.session_state.data])

    with st.sidebar:
        st.image('./logo.png', width=200)  

    st.title("Base de données")
    df = pd.DataFrame(st.session_state.data)
    st.write(df)

    with st.expander("URLs blacklistées"):
        df_blacklist = pd.DataFrame(st.session_state.black_list)
        st.write(df_blacklist)
    

main()