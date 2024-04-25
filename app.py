import streamlit as st
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import pandas as pd
from processing_html import get_mail_from_url

st.set_page_config(layout="wide")


def choose_locations_to_search():
    _, countries_data = get_countries_data()
    countries = list(countries_data.values())
    francophones = ['France', 'Belgique', 'Luxembourg', 'Monaco']
    checkboxes = []
    with st.expander('Pays et Villes'):
        for country in countries:
            if country in francophones:
                checkboxes.append(st.checkbox(country, value=True))
            else:
                checkboxes.append(st.checkbox(country))
    countries_to_search = [country for i, country in enumerate(
        countries) if checkboxes[i]]
    return countries_to_search


@st.cache_data
def get_countries_data():
    with open('./cities_small.json') as f:
        cities_data = json.load(f)

    with open('./countries.json') as f:
        countries_data = json.load(f)

    return cities_data, countries_data


def create_queries(user_query, locations):
    queries = []
    cities_data, countries_data = get_countries_data()
    for country_code, cities in cities_data.items():
        if countries_data[country_code] in locations:
            for city in cities:
                queries.append((user_query, country_code,
                                countries_data[country_code], city))
    return queries


@st.cache_resource
def auth_gspread():
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
    google_service_account_info = st.secrets['google_service_account']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        google_service_account_info, scope)
    client = gspread.authorize(creds)
    return client


def google_search_simple_query(countryCode, query):
    url = 'https://www.googleapis.com/customsearch/v1'
    params = {
        'key': st.secrets['google_search_api_key'],
        'cx': 'd34a74997a27a4205',
        'cr': countryCode,
        'q': query,
    }
    response = requests.get(url, params=params)
    return response.json()


def display_site_info(item):
    already_listed_urls, black_list = get_listed_urls()
    st.subheader(item.get('title'))
    if item.get('link') and item.get('link') in already_listed_urls:
        st.warning('Deja dans la base de données')

    if item.get('link') and item.get('link') in black_list:
        st.error('Dans la liste noire, ne sera pas ajoutée dans la base de données')

    st.write(item.get('snippet'))
    st.write(item.get('link'))
    st.divider()


def add_to_spreadsheet(item, countryName, city, query):
    sheet = get_spreadsheet().sheet1
    already_listed_urls, black_list = get_listed_urls()
    item_link = item.get('link')

    if item_link is None:
        print('No link for --> ', item)
        return

    if item_link not in already_listed_urls and item_link not in black_list:
        try:
            email = get_mail_from_url(item.get('link'))
            sheet.append_row([
                item.get('title'),
                item.get('snippet'),
                item.get('link'),
                email,
                countryName,
                city,
                query
            ])
        except Exception as e:
            print('-----')
            print('Error adding to spreadsheet')
            print(e)


@st.cache_resource(ttl=15)
def get_spreadsheet():
    client = auth_gspread()
    return client.open("base_de_donnees")


@st.cache_resource(ttl=15)
def get_listed_urls():
    sheet = get_spreadsheet().sheet1
    data = sheet.get_all_records()
    already_listed = set([item['URL'] for item in data])
    black_list = sheet = get_spreadsheet().get_worksheet(1).get_all_values()
    black_list = set([elt[0] for elt in black_list[1:]])
    return already_listed, black_list


def display_title_logo():
    with st.sidebar:
        st.image('./logo.png', width=200)
    st.title("Recherches entreprises lo cations de structures gonflables")
    st.subheader("Création de la base de données")


def main():
    display_title_logo()
    user_query = st.text_input("Recherche google")
    locations = choose_locations_to_search()
    if st.button("Search") and user_query:
        compound_queries = create_queries(user_query, locations)
        total_elements = len(compound_queries*10)
        progress_bar = st.progress(1/total_elements, text='Searching')
        index = 1
        for compound_query in compound_queries:
            query, countryCode, countryName, city = compound_query
            st.subheader(" - ".join([query,  city, countryName]))
            with st.expander("Resultats"):
                results = google_search_simple_query(
                    countryCode=countryCode, query=query + " " + city).get("items", [])
                for item in results:
                    progress_bar.progress(
                        index/total_elements, text=f'Recherche : {index} / {total_elements} ({city} - {countryName})')
                    display_site_info(item)
                    add_to_spreadsheet(item, countryName, city, query)
                    index += 1


main()
