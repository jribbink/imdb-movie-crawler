import re
import requests
import shutil
import os
from time import sleep
from seleniumwire import webdriver
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver.support import expected_conditions

from video import Video, QueryInfo, VideoNotFoundException

class ProxyManager:
    class MeasuredProxy:
        def __init__(self, addr):
            self.addr = addr
            self.count = 0

    def __init__(self, file = "config/proxies.txt"):
        def get_proxies(file):
            f = open(file, "r")
            regex = r"(.+:\d+):(.+):(.+)"
            proxies = []
            for line in f:
                result = re.search(regex, line).groups()
                proxies.append("{user}:{password}@{addr}".format(user = result[1], password = result[2], addr = result[0]))
            return proxies

        self.proxies = [ProxyManager.MeasuredProxy(proxy) for proxy in get_proxies(file)]

    @property
    def proxy(self):
        p = min(self.proxies, key = lambda p: p.count)
        p.count += 1

        return p.addr

class WebCrawler:
    def __init__(self, proxy, headless = True, show_images = False):
        seleniumwire_options = {
            "proxy": {
                "http": "http://{}".format(proxy),
                "https": "https://{}".format(proxy),
            }
        }

        chrome_options = Options()
        chrome_options.add_argument("--window-size=1920x1080")

        if(headless): chrome_options.add_argument("--headless")

        if not show_images:
            chrome_prefs = {}
            chrome_options.experimental_options["prefs"] = chrome_prefs
            chrome_prefs["profile.default_content_settings"] = {"images": 2}
            chrome_prefs["profile.managed_default_content_settings"] = {"images": 2}

        self.driver = webdriver.Chrome(options=chrome_options, seleniumwire_options=seleniumwire_options)
        self.wait_for_document()

    def __del__(self):
        self.driver.close()

    def exec_script(self, file, *args):
        f = open(file, "r")
        return self.driver.execute_script(f.read(), *args)

    def wait_for_document(self):
        WebDriverWait(self.driver, 10).until(lambda driver: driver.execute_script("return document.readyState") == "complete")

    def save_image(self, element, dir):
        response = requests.get(element.get_attribute("src"), stream=True)
        os.makedirs(os.path.dirname(dir), exist_ok=True)
        with open(dir, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        del response

    def click_element(self, element, attempts = 5):
        count = 0
        while count < attempts:
            try:
                WebDriverWait(self.driver, 10).until(lambda driver: expected_conditions.element_to_be_clickable(element))
                element.click()
                return
            except WebDriverException as e:
                if ('is not clickable at point' in str(e) and count + 1 < attempts):
                    print("Retrying clicking button...")
                    count += 1
                else:
                    raise e
            
            sleep(1)
                

class VideoCrawler(WebCrawler):
    def __init__(self, headless = True, show_images=False):
        self.__headless = headless
        self.__show_images = show_images
        self.proxy_manager = ProxyManager()
        self.rotate_proxy()

    def rotate_proxy(self):
        if(hasattr(self, "driver")):
            super().__del__()
        super().__init__(self.proxy_manager.proxy, self.__headless, self.__show_images)

    @property
    def knowledge_panel(self):
        return self.driver.find_element_by_xpath("//div[@jscontroller=\"cSX9Xe\"]")

    def get_video(self, video: Video, index):
        try:
            ## Generate query for video
            query = video.query

            search_location = None
            def search_video():
                ## Search for video
                self.driver.get("https://www.google.com")
                self.wait_for_document()

                ## Accept cookies
                agree_element = self.driver.find_elements_by_xpath("//div[contains(string(), \"I agree\") and contains(@class, \"jyfHyd\")]")
                if(self.exec_script("js/findText.js", "Before you continue to Google Search") is not None and len(agree_element) != 0):
                    self.click_element(agree_element[0])

                self.driver.save_screenshot("vid.png")
                search_bar = self.driver.find_element_by_name("q")
                search_bar.send_keys(query.query)
                search_bar.submit()
                self.wait_for_document()
                nonlocal search_location
                search_location = self.driver.current_url
            search_video()

            ## Click on imdb link on knowledge panel
            imdb_url = None
            def click_imdb_link():
                def find_imdb_link():
                    try:
                        return self.exec_script("js/findLink.js", r"https://www.imdb.com/title/.+/", self.knowledge_panel)
                    except NoSuchElementException:
                        return None
                
                imdb_link = find_imdb_link()
                if imdb_link is None:
                    def attempt_next_query():
                        query.next_query()
                        if query.query is not None:
                            search_video()
                        else:
                            self.driver.save_screenshot("ERROR_" + query.title + ".png")
                            raise VideoNotFoundException()
                    
                    # Check if this is a series if imdb link is not found
                    movie_links = self.driver.find_elements_by_css_selector("wp-grid-view [data-attrid=\"kc:/film/film_series:films\"]")
                    if(len(movie_links) > 0):
                        ## If film series and no year is given, use first film
                        print("Warning: Used first film without year")
                        self.click_element(movie_links[0])
                        try:
                            WebDriverWait(self.driver, 10).until(lambda driver: find_imdb_link() is not None)
                        except TimeoutException:
                            attempt_next_query()
                        return click_imdb_link()
                    else:
                        attempt_next_query()
                        return click_imdb_link()
                else:
                    nonlocal imdb_url
                    imdb_url = imdb_link.get_attribute("href")

                self.click_element(imdb_link)
                self.wait_for_document()
            click_imdb_link()

            ## Save imdb info
            description = self.driver.find_element_by_class_name("GenresAndPlot__TextContainerBreakpointXL-cum89p-2").text
            directors = self.exec_script("js/getIMDbCredits.js", "Director")
            stars = self.exec_script("js/getIMDbCredits.js", "Stars")

            ## Click on poster image
            poster_image_link = self.driver.find_element_by_css_selector(".Poster__CelPoster-sc-6zpm25-0 .ipc-lockup-overlay")
            self.click_element(poster_image_link)
            self.wait_for_document()

            ## Save poster image
            imdb_poster_query = self.driver.find_elements_by_class_name("MediaViewerImagestyles__PortraitImage-sc-1qk433p-0")
            poster_image = None
            if len(imdb_poster_query) > 0:
                poster_image = imdb_poster_query[0]
            else:
                ## Backtrack to knowledge panel
                self.driver.get(search_location)
                self.wait_for_document()
                # Get google image link
                image_link = self.driver.find_element_by_css_selector(".kAOS0")
                self.click_element(image_link)
                self.wait_for_document()

                # Get google image current featured image
                feature_image = self.driver.find_element_by_css_selector("[jsname=\"CGzTgf\"] [jsname=\"HiaYvf\"]")
                poster_image = feature_image

            self.save_image(poster_image, "images/{:05}_{}.png".format(index, query.title))

            return {
                "description": description,
                "directors": directors,
                "stars": stars,
                "image": "images/{:05}_{}.png".format(index, query.title),
                "imdb_url": imdb_url
            }
        finally:
            self.rotate_proxy()