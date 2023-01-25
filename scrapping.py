import json
import concurrent.futures
from datetime import datetime
from bs4 import BeautifulSoup
from time import sleep
from typing import List, Tuple, Any, Generator
from typeguard import typechecked
import argparse

from selenium import webdriver
from selenium.common import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Params
WORKERS = 2


@typechecked
class YouTubeVideoScrapper():
    def __init__(self) -> None:
        # DRIVER
        op = Options()
        op.headless = False
        self.driver = webdriver.Chrome(options=op)
        self.driver.set_window_size(800, 1100)
        self.driver.implicitly_wait(10)

        self.wait = WebDriverWait(self.driver, 20)

        self.cookies_accepted = False

    def go(self, video_id: str) -> None:
        """
        Aller à une url d'une page
        :param video_id: l'id de la video youtube
        """

        # OPEN PAGE
        self.driver.get(f"https://www.youtube.com/watch?v={video_id}")
        self.video_id = video_id
        self.current_url = self.driver.current_url
        print(f">>> {self.video_id}...")

        # CLICK COOKIES
        if not self.cookies_accepted:
            self.__click_accept_cookies()
        sleep(5)
        # CLICK DESCRIPTION
        self.__click_show_more_description()
        sleep(0.2)
        # SCROLL DOWN
        self.__scroll_down(scroll_pause_time=1.5)
        sleep(1)

        self.soup = BeautifulSoup(str((self.driver.page_source).encode('utf-8')), 'lxml')

    def __click_accept_cookies(self) -> None:
        """
        fermer la fenêtre des cookies
        """
        button = self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="content"]/div[2]/div[6]/div[1]/ytd-button-renderer[2]/yt-button-shape/button')))
        button.click()
        self.cookies_accepted = True

    def __click_show_more_description(self) -> None:
        """
        cliquer sur le bouton pour voir toute la description
        :return:
        """
        # button = self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="expand"]')))
        button = self.driver.find_element(By.XPATH,
                                          '/html/body/ytd-app/div[1]/ytd-page-manager/ytd-watch-flexy/div[5]/div[1]/div/div[2]/ytd-watch-metadata/div/div[3]/div[1]/div/ytd-text-inline-expander/tp-yt-paper-button[1]')
        button.click()

    def __scroll_down(self, scroll_pause_time: float = 1, k_scrolls: int = 3) -> None:
        """
        Scroller tout en bas de la page
        :param scroll_pause_time: temps de pause entre chaque scrollement
        :param k_scrolls: nombre de scrollement
        :return:
        """
        # Get scroll height
        print(f"  > {self.video_id}... let's scrolling... ")
        last_height = self.driver.execute_script("return document.documentElement.scrollHeight")
        k = 0
        while True:
            # Scroll down to bottom
            self.driver.execute_script("window.scrollTo(0, arguments[0]);", last_height)
            # Wait to load page
            sleep(scroll_pause_time)

            # Calculate new scroll height and compare with last scroll height
            new_height = self.driver.execute_script("return document.documentElement.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            k += 1
        print(f"  > {self.video_id}ok i'am at the bottom (after {k} scrolling) !")

    def get_all_infos(self) -> dict:
        """
        :return: dictionnaires avec toutes les infos issue du scrapping
        """
        result = {"video_id": self.video_id, "video_url": self.current_url}

        div_above_the_fold = self.soup.find("div", {"id": "above-the-fold"})
        div_comments = self.soup.find("ytd-comments", {"id": "comments"})

        # TITLE
        title_item = div_above_the_fold.find("h1", {'class': 'style-scope ytd-watch-metadata'})
        result["video_title"] = title_item.text

        # AUTHOR
        author_item = div_above_the_fold.find("a", {'class': 'yt-simple-endpoint style-scope yt-formatted-string'})
        result["video_author_name"] = author_item.text
        result["video_author_url"] = f'https://www.youtube.com/{author_item["href"]}'

        # VIEWS & DATE
        spans = div_above_the_fold.find("div", {'id': "info-container"}).find_all("span")
        result["video_views"] = spans[0].text.split(" ")[0]
        result["video_published_date"] = spans[-1].text

        # DESCRIPTION
        desc_item = div_above_the_fold.find("ytd-text-inline-expander", {"id": "description-inline-expander"})
        result['video_description_text'] = desc_item.text

        # LINKS DESCRIPTION
        links = [{"text": link.text, "href": link["href"]} for link in desc_item.find_all("a")]
        result['video_description_links'] = links

        # ID VIDEO
        # result['video_id'] = self.current_url.split("?v=")[-1]

        # COMMENTS
        nb_comments_item = div_comments.find("h2", {"id": "count"}).find("span")
        result["video_nb_comments"] = nb_comments_item.text

        div_all_comments = div_comments.find("div", {"id": "contents"})

        comments_result = []
        for comment_div in div_all_comments.find_all("ytd-comment-thread-renderer"):
            content_item = comment_div.find("yt-formatted-string", {"id": "content-text"})
            vote_count_item = comment_div.find("span", {"id": "vote-count-middle"})
            a_item = comment_div.find("a", {"id": "author-text"})

            comments_result.append(
                {"author_text": a_item.text.strip(), "author_href": a_item["href"], "content_text": content_item.text,
                 "vote_count": vote_count_item.text})

        result["video_comments"] = comments_result
        print(f">>> {self.video_id}... done.")
        return result


@typechecked
def read_input_json(input_json_file_path: str = "input.json") -> List[str]:
    with open(input_json_file_path, "r") as f:
        data = json.load(f)
    return data["videos_id"]


@typechecked
def write_output_json(data: List[dict], output_file_path: str = "output.json") -> None:
    date_time = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")

    output_dict = {"date_time": date_time, "data": data}
    with open(output_file_path, "w") as f:
        json.dump(output_dict, f, indent=4)
    print(f"*******\njSON OUTPUT FILE : {output_file_path}\n*******")


@typechecked
def chunks(lst: List[Any], n: int) -> Generator[List[Any], None, None]:
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


@typechecked
def start_scraping(videos_id: list) -> List[dict]:
    scrapping_results = []
    scrapper = YouTubeVideoScrapper()
    for video_id in videos_id:
        scrapper.go(video_id=video_id)
        try:
            scrap_infos = scrapper.get_all_infos()
        except Exception as e:
            print(f"ERROR : {str(e)}")
            break
        else:
            scrapping_results.append(scrap_infos)

    return scrapping_results


def main() -> None:
    # Args
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', help='Input JSON file with URLs', required=True)
    parser.add_argument('--output', help='Output JSON file with data', required=True)
    argdict = vars(parser.parse_args())
    INPUT_PATH = argdict['input']
    OUTPUT_PATH = argdict['output']

    videos_id = read_input_json(INPUT_PATH)
    print(f"*******\nIDs TO SCRAP : {videos_id}\n*******")

    p = len(videos_id) // WORKERS
    p = p if len(videos_id) % WORKERS == 0 else p + 1
    videos_id_chunks = list(chunks(videos_id, p))
    print([len(v) for v in videos_id_chunks])

    results: List[dict] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as executor:
        for result in executor.map(start_scraping, videos_id_chunks):
            results += result

    write_output_json(data=results, output_file_path=OUTPUT_PATH)


if __name__ == "__main__":
    main()
