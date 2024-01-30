import requests
from bs4 import BeautifulSoup
import urllib.parse

def getmainpagedata(data_wydania:int, obszary:int):
    "Otrzymaj dane ze strony internetowej"

    # Adres URL strony z parametrami
    urlcore = 'https://www.osw.waw.pl/pl/publikacje?'
    parametry = {"f[0]":f"data_wydania:{data_wydania}", "f[1]":f"obszary:{obszary}"} #TODO Dodać obsługę zmiany strony strony zbiorczej (page) 

    # Kompletny URL
    url = urlcore + urllib.parse.urlencode(parametry)

    # Pobieramy zawartość strony
    response = requests.get(url, timeout=1000)

    if response.status_code == 200:
        return response.text
    else:
        raise ConnectionError(f'Błąd podczas dostępu do strony: {response.status_code}')

def getsubpagedata(koncowka):
    "Otrzymaj zawartość podstrony z końcówki adresu URL"
    # Adres URL strony
    urlcore = 'https://www.osw.waw.pl'
    url = urlcore + koncowka

    # Pobieramy zawartość strony
    response = requests.get(url, timeout=1000)

    if response.status_code == 200:
        return response.text
    else:
        raise ConnectionError(f'Błąd podczas dostępu do strony: {response.status_code}')
 
# getpagedata(2012, 20) | 2012 -> rok / 20 -> obszar (tu Rosja)
   
def extract_links(html):
    "Pobierz linki do artykułów ze strony"
    soup = BeautifulSoup(html, 'html.parser')

    # Znajdowanie wszystkich elementów <h3> z klasą 'field-content'
    h3_tags = soup.find_all('h3', class_='field-content')

    # Zbieranie linków z atrybutu 'href' dla znalezionych tagów <a>
    links = [a['href'] for h3 in h3_tags for a in h3.find_all('a', href=True)]

    return links

def extract_content(html):
    "Pobierz zawartość artykułów ze strony"
    soup = BeautifulSoup(html, 'html.parser')

    content = soup.find("article")

    # Pobieranie tytułu
    title = content.find('div', class_='field field--name-field-display-title field--type-string field--label-hidden field--item').get_text(strip=True)

    # Pobieranie autora
    author = content.find('div', class_='field field--name-field-autorzy-erf field--type-entity-reference field--label-hidden field--items').get_text(strip=True)

    # Szukanie reszty tekstu (wszystkiego poza tytułem i autorem)
    restofcontent = content.find('div', class_='field field--name-body field--type-text-with-summary field--label-hidden field--item').get_text(" ", strip=True)

    return title, author, restofcontent

# Otrzymywanie zawartości kolejnych akrtkółow na jednej stronie zbiorczej
# links = extract_links(getmainpagedata(2012, 20))
# for link in links:
#     print(extract_content(getsubpagedata(link)))
#     input("STOP!")

