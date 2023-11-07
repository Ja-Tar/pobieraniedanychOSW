import requests
from bs4 import BeautifulSoup

# Adres URL strony, którą chcemy scrapować
url = 'https://www.osw.waw.pl/pl/publikacje?'

# Pobieramy zawartość strony
response = requests.get(url, timeout=10000)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    titles = soup.find_all('h3')
    
    # Wydrukujmy zawartość każdego znalezionego tytułu
    for title in titles:
        print(title.get_text().strip())
else:
    print(f'Błąd podczas dostępu do strony: {response.status_code}')
