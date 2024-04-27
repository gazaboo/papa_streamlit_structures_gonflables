from urllib.parse import urlparse
import streamlit as st
import requests
# import gspread
# from oauth2client.service_account import ServiceAccountCredentials
import json
import pandas as pd
from meta_data_handler import get_metadata
from processing_html import get_mail_from_url

from authenticators import auth_gspread


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
    with open('./cities_medium.json') as f:
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


def should_be_scraped(item_link):
    already_listed_urls, black_list = get_listed_urls()
    netloc = urlparse(item_link).netloc
    already_done = netloc in already_listed_urls or netloc in black_list
    return not already_done


def add_to_spreadsheet(item, countryName, city, query):
    sheet = get_spreadsheet_object()
    item_link = item.get('link')

    if should_be_scraped(item_link):
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


@st.cache_resource(ttl=30)
def get_spreadsheet_data():
    client = auth_gspread()
    id = st.session_state.current_metadata['id']
    return client.open_by_key(id).get_worksheet(0).get_all_records()


@st.cache_resource(ttl=30)
def get_black_list():
    client = auth_gspread()
    id = st.session_state.current_metadata['id']
    sheet = client.open_by_key(id)
    if len(sheet.worksheets()) > 1:
        return sheet.get_worksheet(1).get_all_values()
    return "Aucune"


@st.cache_resource(ttl=30)
def get_spreadsheet_object():
    client = auth_gspread()
    id = st.session_state.current_metadata['id']
    return client.open_by_key(id).get_worksheet(0)


@st.cache_resource(ttl=30)
def get_listed_urls():
    data = get_spreadsheet_data()
    already_listed = set([urlparse(item['URL']).netloc for item in data])
    black_list = get_black_list()
    black_list = set([urlparse(elt[0]).netloc for elt in black_list[1:]])
    return already_listed, black_list


def is_in_database(item):
    already_listed_urls, _ = get_listed_urls()
    return urlparse(item.get('link')).netloc in already_listed_urls


def is_blacklisted(item):
    _, black_list = get_listed_urls()
    return urlparse(item.get('link')).netloc in black_list


def get_history_of_used_keywords():
    data = get_spreadsheet_data()
    keywords = set([item['Mots clés'] for item in data])
    return keywords
