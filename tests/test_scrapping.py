
import pytest
from scrapping import YouTubeVideoScrapper

@pytest.fixture
def scrapper():
    # All setup for the scrapper here
    return YouTubeVideoScrapper()

def test_can_go_to_page(scrapper):
    scrapper.go("YbpKMIUjvK8")
    assert scrapper.current_url == "https://www.youtube.com/watch?v=YbpKMIUjvK8"

def test_click_cookies(scrapper):
    pass

def test_scrolling_at_the_bottom(scrapper):
    pass

