import time

from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup
import requests
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import re


def extraction(soup, browser):
    """
    Given the url of one habitaclia page, this function extracts all basic info for the 15 flats in it.
    It creates a flat instance for each one of it, the additional info it's added in the second extraction function

    :param url: URL of an habitaclia page (usually has 15 flats in it)
    :param flats_visited: track of flats loaded from pickle file in order to not treat them again.
    :return: list of the 15 flats created
    """

    all_props = soup.find(id='properties').find_all('div', class_='mb-4 px-3 col')
    all_rows = []

    for indx, prop in enumerate(all_props):
        link = prop.find('a')['href']

        browser.get(url=link)

        delay = 5
        WebDriverWait(browser, delay).until(
            EC.visibility_of_element_located((By.ID, "owner")))
        soup = BeautifulSoup(browser.page_source, "html.parser")

        price = int(soup.find('span', class_='price badge badge-primary').text.split('/')[0][:-1])

        attrs = soup.find(id='apartment-summary').find_all('p')

        location = attrs[0].text.strip()
        date = attrs[1].text.strip().split(' ')[-1]
        room = int(attrs[2].text.strip()[0])
        couple = 'not' not in attrs[3].text.strip()

        owner_desc = soup.find(id='owner')
        desc = owner_desc.find('p').find_all(text=True)
        full_desc = ''
        for text in desc:
            full_desc += re.sub(r'[\n\r]', '', (text.strip()))

        owner_info = owner_desc.find('h1').text[:-4].split(',')
        owner_name = owner_info[0]
        owner_age = owner_info[1][1:]

        row = {
            'URL': link,
            'price': price,
            'location': location,
            'date': date,
            'rooms available': room,
            'couple': couple,
            'description': full_desc,
            'owner name': owner_name,
            'owner age': owner_age
        }

        print()
        print(location)
        print(price, '€')
        print("Couple:", couple)
        print("Owner:", owner_name + ',',owner_age)
        print()

        all_rows.append(row)

    return all_rows


def main():
    print("hello world")

    base_url = 'https://www.depisoenpiso.com/find-places.html?ciudad=Barcelona'
    browser = webdriver.Chrome('chromedriver.exe')
    browser.get(url=base_url)

    delay = 4  # seconds
    try:
        WebDriverWait(browser, delay).until(EC.visibility_of_element_located((By.XPATH, "//*[starts-with(@id, 'prop-')]")))
        time.sleep(2)
        soup = BeautifulSoup(browser.page_source, "html.parser")

        total_pages = int(soup.find('ul', class_="pagination mx-auto").find_all('li')[-2].text)
        all_rows = []

        for numpage in range(total_pages):
            print("Reading page " + str(numpage + 1) + " of " + str(total_pages))

            if numpage == 0:
                rows = extraction(soup, browser)
                all_rows = all_rows + rows

            else:
                url = base_url + "&pagina=" + str(numpage)
                browser.get(url=url)
                WebDriverWait(browser, delay).until(
                    EC.visibility_of_element_located((By.XPATH, "//*[starts-with(@id, 'prop-')]")))
                soup = BeautifulSoup(browser.page_source, "html.parser")

                rows = extraction(soup, browser)
                all_rows = all_rows + rows

        df = pd.DataFrame(all_rows)
        df.to_csv("PisEnPis.csv", sep='*', index=False)

    except TimeoutException:
        print("error")
        "Loading took too much time!"












if __name__ == "__main__":
    main()