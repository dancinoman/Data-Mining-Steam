# Import information from a steam web site and save it on a csv file

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import chromedriver_binary
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as ec
from bs4 import BeautifulSoup
import csv
import time

def scrape_page(year):
    driver = webdriver.Chrome()
    driver.get(f"https://steamdb.info/stats/gameratings/{year}/")

    print('Get on web site')
    wait = WebDriverWait(driver, 15).until(lambda x : x.find_element(By.ID, 'dt-length-0'))
    get_input = Select(driver.find_element(By.ID, 'dt-length-0'))
    get_input.select_by_visible_text('All (slow)')

    print('Element has been selected')
    print('The page is loading')

    wait = WebDriverWait(driver, 5)
    wait.until(ec.visibility_of_element_located((By.XPATH, "//div[@id='main']")))

    print('Info located ready to fetch...')

    #Using beautiful soup to get the list of games
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    games_list = soup.find_all('tr', class_='app')


    games = []

    for game in games_list:
        name = game.find('a', class_='b').text.strip()

        # Get another list inside of the element of list
        elements = game.find_all('td', class_ = 'dt-type-numeric')

        price = elements[2].text.replace('CDN$', '').strip()
        rating = elements[3].text.replace('%', '').strip()
        release_date = elements[4].text.strip()
        followers = elements[5].text.replace(',', '').strip()
        peak_online = elements[7].text.replace(',', '').strip()

        games.append({
            'name'         : name,
            'price'        : price,
            'rating'       : rating,
            'release date' : release_date,
            'followers'    : followers,
            'max peak'     : peak_online
        })

    print(f' Writing {len(games)} element(s)')
    with open(f'data/csv/games_top_{year}.csv', 'w') as file:
        writer = csv.DictWriter(file, fieldnames= games[0].keys())
        writer.writeheader()
        writer.writerows(games)
    print('1 page done successfully')
    driver.quit()

for year in range(2023,2024):
    scrape_page(year)
