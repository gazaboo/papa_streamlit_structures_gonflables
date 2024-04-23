import re 
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup

def extract_emails_from_html(html_content):
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, html_content)
    return emails

def download_webpage(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(e)
        return None

def get_mail_from_url(url):
    try :
        html = download_webpage(url)

        if html is not None :
            email = extract_emails_from_html(html) 
            if email and len(email) > 0:
                return email[0]

            links_to_visit_next = get_url_from_same_domain(url, html)
            links_to_visit_next = reorder_links(links_to_visit_next)
            if len( links_to_visit_next) > 0:
                for link in links_to_visit_next:
                    html = download_webpage(link)
                    email = extract_emails_from_html(html)
                    if email and len(email) > 0:
                        return email[0]
            
            return " "
        return " "
    except Exception as e :
        print(e)
        return " "


def get_url_from_same_domain(url, html):
    base_domain = urlparse(url).netloc
    links = extract_all_links(html)
    links_in_same_domain = [link for link in links if urlparse(url).netloc == base_domain]
    return links_in_same_domain

def extract_all_links(html):
    soup = BeautifulSoup(html, 'html.parser')
    links = []
    for link in soup.find_all('a'):
        href = link.get('href')
        if href:
            links.append(href)
    return links

def reorder_links(links):
    return list(sorted(links, key= lambda x: "contact" not in x.lower()))

