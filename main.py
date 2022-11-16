import pandas as pd
import numpy as np
import requests
from selenium import webdriver
from selenium.common import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import json
from bs4 import BeautifulSoup
from time import sleep
from typing import List,Tuple
# %%
URLS = ["https://www.youtube.com/watch?v=Wu919BSzEbY", "https://www.youtube.com/watch?v=nU5MSi5goW0",
        "https://www.youtube.com/watch?v=8fqcivpFBio&t=568s", "https://www.youtube.com/watch?v=2ge0oJxlU68"]


class YouTubeVideoScrapper():

    def __init__(self) -> None:
        # DRIVER
        op = Options()
        op.headless = False
        self.driver = webdriver.Chrome(options=op)
        self.driver.set_window_size(800,1100)
        self.driver.implicitly_wait(10)

        self.wait = WebDriverWait(self.driver,20)

    def go(self, ytb_video_url : str) -> None:

        self.ytb_video_url = ytb_video_url
        # OPEN PAGE
        self.driver.get(self.ytb_video_url)
        # CLICK COOKIES
        self.__click_accept_cookies()
        sleep(5)
        # CLICK DESCRIPTION
        self.__click_show_more_description()
        sleep(1)
        # SCROLL DOWN
        self.__scroll_down()
        sleep(1)
        self.soup = BeautifulSoup(str(self.driver.page_source), 'lxml')




    def __click_accept_cookies(self)-> None:
        button = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="content"]/div[2]/div[6]/div[1]/ytd-button-renderer[2]/yt-button-shape/button')))
        button.click()

    def __click_show_more_description(self) -> None:

        #button = self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="expand"]')))
        button = self.driver.find_element(By.XPATH, '/html/body/ytd-app/div[1]/ytd-page-manager/ytd-watch-flexy/div[5]/div[1]/div/div[2]/ytd-watch-metadata/div/div[3]/div[1]/div/ytd-text-inline-expander/tp-yt-paper-button[1]')
        button.click()

    def __scroll_down(self,scroll_pause_time = 1,k_scrolls=3):

        # Get scroll height
        last_height = self.driver.execute_script("return document.documentElement.scrollHeight")
        k = 0
        while k < k_scrolls:
            # Scroll down to bottom
            self.driver.execute_script("window.scrollTo(0, arguments[0]);", last_height)
            # Wait to load page
            sleep(scroll_pause_time)

            # Calculate new scroll height and compare with last scroll height
            new_height = self.driver.execute_script("return document.documentElement.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            k+=1
        print("k",k)

    def get_title(self,how_many=3) -> str:
        print(how_many)
        if how_many > 0:
            try:
                h1 = self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="title"]/h1')))
            except StaleElementReferenceException:
                return self.get_title(how_many-1)
            else:
                return h1.text
        else:
            return None

    def get_author(self) -> Tuple[str,str]:
        a = self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#text > a")))
        return a.text, a.get_attribute('href')

    def get_likes(self) -> str:
        span = self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#segmented-like-button > ytd-toggle-button-renderer > yt-button-shape > button > div.cbox.yt-spec-button-shape-next--button-text-content > span")))
        #span = self.driver.find_element(By.CSS_SELECTOR, "#segmented-like-button > ytd-toggle-button-renderer > yt-button-shape > button > div.cbox.yt-spec-button-shape-next--button-text-content > span")

        return span.text


    def get_description(self) -> str:

        sleep(10)
        pass

    def get_links_from_description(self)-> List[str]:
        pass

    def get_id_video(self)-> str:
        pass

    def get_comments(self)-> List[dict]:
        pass
        # GET COMMENTS



    def get_all_infos(self) -> dict:
        print("get_all_infos")
        #page_source = self.driver.page_source.encode('utf-8').strip()


        div = self.soup.find("div", {"id":"above-the-fold"})

        title_item = div.find("h1",{'class' : 'style-scope ytd-watch-metadata'})
        print(title_item.text)
        author_item = div.find("a",{'class' : 'yt-simple-endpoint style-scope yt-formatted-string'})
        print(author_item.text,f'https://www.youtube.com/{author_item["href"]}')

        #result['description'] = self.get_description()
        #print(result)


        return result

#%%
scrapper = YouTubeVideoScrapper()
scrapper.go(URLS[0])
#%%
video_infos = scrapper.get_all_infos()
#%%
def main()-> None:
    scrapper = YouTubeVideoScrapper()
    scrapper.go(URLS[0])
    video_infos = scrapper.get_all_infos()


#%%
r"""
def main_0():
    driver = webdriver.Chrome()
    for url in URLS:
        driver.get('{}/videos?view=0&sort=p&flow=grid'.format(url))
        content = driver.page_source.encode('utf-8').strip()
        soup = BeautifulSoup(content, 'lxml')
        titles = soup.findAll('a', id='video-title')
        views = soup.findAll('span', class_='style-scope ytd-grid-video-renderer')
        video_urls = soup.findAll('a', id='video-title')
        print('Channel: {}'.format(url))
        i = 0  # views and time
        j = 0  # urls
        for title in titles[:10]:
            print('\n{}\t{}\t{}\thttps://www.youtube.com{}'.format(title.text, views[i].text, views[i + 1].text,
                                                                   video_urls[j].get('href')))
            i += 2
            j += 1
"""
if __name__ == "__main__":
    pass