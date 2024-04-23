import streamlit as st
import requests

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import pandas as pd

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
    st.session_state['data'] = st.session_state.sheet.get_all_records()    
    st.session_state['already_listed_url'] = set([item['Link'] for item in st.session_state.data])

    st.title("Recherches entreprises locations de structures gonflables")
    st.subheader("Création de la base de données")
    st.image('./logo.png', width=150)

    df = pd.DataFrame(st.session_state.data)
    st.write(df)

main()