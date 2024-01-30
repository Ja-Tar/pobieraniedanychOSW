import json
import os
import time
import unicodedata
from datetime import datetime

import requests
from bs4 import BeautifulSoup


def load_json(file_path):
    """
    Load a JSON file from the given file path and return the parsed JSON data.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        list: The parsed JSON data, or an empty list if the file is not found or cannot be parsed.
    """
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []


def save_json(data, file_path):
    """
    Save the given data to a JSON file at the specified file path.

    Args:
        data: The data to be saved to the JSON file.
        file_path: The path to the JSON file.

    Returns:
        None
    """
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def getmainpagedata(page: int):
    """
    Get data from the main page.

    :param page: int, the page number
    :return: str, the text content of the page
    """

    # Adres URL strony z parametrami
    urlcore = "http://en.kremlin.ru/events/president/transcripts"

    # Kompletny URL
    url = urlcore + "/page/" + str(page)

    # Pobieramy zawartość strony
    response = requests.get(
        url, timeout=120, headers={"User-Agent": "Mozilla/5.0", "Accept": "text/html"}
    )

    if response.status_code == 200:
        return response.text
    else:
        raise ConnectionError(f"Błąd podczas dostępu do strony: {response.status_code}")


def getsubpagedata(koncowka):
    """
    Function to get data from a subpage.

    :param koncowka: The endpoint of the URL.
    :return: The text content of the response.
    :raises ConnectionError: If the response status code is not 200.
    """

    # Adres URL strony
    urlcore = "http://en.kremlin.ru"
    url = urlcore + koncowka

    # Pobieramy zawartość strony
    response = requests.get(
        url, timeout=120, headers={"User-Agent": "Mozilla/5.0", "Accept": "text/html"}
    )

    if response.status_code == 200:
        return response.text
    else:
        raise ConnectionError(f"Błąd podczas dostępu do strony: {response.status_code}")

def extract_links(html):
    """
    Extracts links from the given HTML content and returns a list of the extracted links.
    :param html: The HTML content from which links are to be extracted.
    :return: A list of strings representing the extracted links.
    """

    soup = BeautifulSoup(html, "html.parser")

    # Search for h3 tags with class "hentry__title"
    h3_tags = soup.find_all("h3", class_="hentry__title")

    # Extract links from the h3 tags
    _links = [a["href"] for h3 in h3_tags for a in h3.find_all("a", href=True)]

    return _links


def extract_content(html):
    """
    Extracts title, summary, date, time, place, and the rest of the content from the given HTML.

    Args:
        html (str): The HTML content to be parsed.

    Returns:
        tuple: A tuple containing the title (str), summary (str), date (str), time (str), place (str), and the rest of the content (str).
    """

    soup = BeautifulSoup(html, "html.parser")

    content = soup.find("article")

    # Pobieranie tytułu
    title = content.find("h1", class_="entry-title p-name").get_text(strip=True)
    title = unicodedata.normalize("NFKC", title).replace("\n", " ")

    # Pobieranie autora
    summary = content.find("div", class_="read__lead entry-summary p-summary").get_text(
        strip=True
    )
    summary = unicodedata.normalize("NFKC", summary).replace("\n", " ")

    # Pobieranie daty, czasu i miejsca
    date = content.find("time", class_="read__published").get_text(strip=True)
    timel = content.find("div", class_="read__time").get_text(strip=True)
    place = content.find("div", class_="read__place p-location")
    if place is None:
        place = "No location"
    else:
        place = place.get_text(strip=True)
        place = unicodedata.normalize("NFKC", place).replace("\n", " ")

    # Szukanie reszty tekstu (wszystkiego poza tytułem i autorem)
    restofcontent = content.find(
        "div", class_="entry-content e-content read__internal_content"
    ).get_text(" ", strip=True)
    restofcontent = unicodedata.normalize("NFKD", restofcontent).replace("\n", " ")

    return title, summary, date, timel, place, restofcontent


def getdata(target_year):
    """
    Retrieves data from web pages until the target year is reached, and saves the content and links in JSON files.
    Memory inefficient. To be improved.

    Args:
        target_year (int): The target year until which the content should be retrieved.

    Returns:
        None
    """
    allcontent_path = "allcontent.json"
    linki_path = "linki.json"

    allcontentpage = load_json(allcontent_path)
    stop = False
    alllinks = load_json(linki_path)

    for page_number in range(1, 100):  # Max page number is 100
        if stop:
            break

        links = extract_links(getmainpagedata(page_number))

        print(f"LINKS for Page {page_number}:")
        print(links)
        print("==============")
        time.sleep(2)

        if not links:
            print("No more pages to check. Exiting.")
            break

        for link in links:
            # check if the linki.json file contains the link
            if link in alllinks:
                print(f"Skipping {link} because it already exists in linki.json")
                continue

            contentpage = extract_content(getsubpagedata(link))
            print(contentpage[0])
            print(contentpage[2])

            # Extract the year from the date
            year_from_content = datetime.strptime(contentpage[2], "%B %d, %Y").year

            # check if the year from the content matches the target year
            if year_from_content == (target_year - 1):
                print("==============")
                print(f"Found all content until {target_year}. Stopping.")
                stop = True
                break

            allcontentpage.append(contentpage)
            alllinks.append(link)
            time.sleep(1)
            print("==============")
            print("NEXT!")
            print("==============")

    # create a json file for content
    save_json(allcontentpage, allcontent_path)

    # create a json file for links
    save_json(alllinks, linki_path)


def main():
    """
    A function that calls the getdata function with the parameter 2021.
    """
    getdata(2021)  # Change the year here


if __name__ == "__main__":
    main()
