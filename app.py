import streamlit as st
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import pandas as pd
from processing_html import get_mail_from_url

st.set_page_config(layout="wide")

def create_queries(user_query):
    queries = [] 
    with open('./cities.json') as f:
        cities_data = json.load(f)

    for country_code, cities in cities_data.items():
        for city in cities:
            queries.append((country_code, user_query + ' ' + city))
    return queries

# Function to authenticate and create a client.
def auth_gspread():
    scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
    google_service_account_info = st.secrets['google_service_account']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(google_service_account_info, scope)
    client = gspread.authorize(creds)
    return client

# Function to perform the Google search
def google_search_simple_query(countryCode, query):
    url = 'https://www.googleapis.com/customsearch/v1'
    params = {
        'key': st.secrets['google_search_api_key'],
        'cx': 'd34a74997a27a4205',
        'cr' : countryCode,
        'q': query,
    }
    response = requests.get(url, params=params)
    return response.json()

def display_site_info(item):
    st.subheader(item.get('title'))
    if item.get('link') and item.get('link') in st.session_state.already_listed_url : 
        st.warning('Deja dans la base de données') 
    st.write(item.get('snippet'))
    st.write(item.get('link'))
    st.divider()


def add_to_spreadsheet(item):
    if item.get('link') is not None:
        if item.get('link') and item.get('link') not in st.session_state.already_listed_url : 
            try :
                email = get_mail_from_url( item.get('link') )
                st.session_state.sheet.append_row([
                    item.get('title'),
                    item.get('snippet'),
                    item.get('link'), 
                    email
                ])
            except Exception as e:
                print(e)


# Streamlit user interface
def main():

    # init everything
    client = auth_gspread()
    st.session_state['sheet'] = client.open("base_de_donnees").sheet1 
    st.session_state['data'] = st.session_state.sheet.get_all_records()    
    st.session_state['already_listed_url'] = set([item['Link'] for item in st.session_state.data])

    with st.sidebar:
        st.image('./logo.png', width=200)

    st.title("Recherches entreprises locations de structures gonflables")
    st.subheader("Création de la base de données")

    user_query = st.text_input("Enter the search query")
    if st.button("Search") and user_query:
        compound_queries = create_queries(user_query)
        for compound_query in compound_queries:
            st.subheader(" - ".join(compound_query))
            results = google_search_simple_query(*compound_query).get("items", [])
            for item in results:
                display_site_info(item)
                add_to_spreadsheet(item)

main()