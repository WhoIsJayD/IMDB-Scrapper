import requests
import scrapy
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from queue import Queue
from requests.adapters import HTTPAdapter
from scrapy.crawler import CrawlerProcess
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from urllib3.util.retry import Retry


class IMDbTMDbSpider(scrapy.Spider):
    name = 'advance_scrapper'
    allowed_domains = ['imdb.com', 'themoviedb.org']
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'CONCURRENT_REQUESTS': 100,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 50,
        'CONCURRENT_REQUESTS_PER_IP': 50,
        'DOWNLOAD_DELAY': 0.5,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'LOG_LEVEL': 'INFO',
        'RETRY_TIMES': 5,
        'REACTOR_THREADPOOL_MAXSIZE': 20,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 60,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 10,
        'AUTOTHROTTLE_DEBUG': False,
        'DOWNLOAD_TIMEOUT': 30,
        'COOKIES_ENABLED': False,
        'TELNETCONSOLE_ENABLED': False,
        'FEEDS': {
            'movies.json': {
                'format': 'json',
                'overwrite': False,
            },
            'movies.csv': {
                'format': 'csv',
                'overwrite': False,
            },
        }
    }

    def __init__(self, tmdb_api_key, num_instances=5, start=2000, end=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tmdb_api_key = tmdb_api_key
        self.num_instances = num_instances
        self.base_tmdb_url = "https://api.themoviedb.org/3"
        self.year_month_queue = Queue()
        self.executor = ThreadPoolExecutor(max_workers=self.num_instances)
        self.scraped_years_months = set()
        self.scraped_imdb_ids = set()
        self.populate_year_month_queue(start, end)
        self.session = self.create_session()

    def create_session(self):
        session = requests.Session()
        retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[429, 500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retries, pool_connections=100000, pool_maxsize=100000)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    def start_requests(self):
        yield scrapy.Request(url='https://www.imdb.com', callback=self.parse, dont_filter=True)

    def parse(self, response):
        self.logger.info("Starting to scrape...")
        futures = []
        for _ in range(self.num_instances):
            futures.append(self.executor.submit(self.scrape_instance))
        for future in as_completed(futures):
            yield from future.result()

    def scrape_instance(self):
        driver = webdriver.Chrome()
        try:
            while not self.year_month_queue.empty():
                year, month = self.year_month_queue.get()
                if (year, month) in self.scraped_years_months:
                    continue
                last_day = (datetime(year, month, 28) + timedelta(days=4) - timedelta(days=1)).day
                url = f'https://www.imdb.com/search/title/?title_type=feature,tv_series&release_date={year}-{month:02d}-01,{year}-{month:02d}-{last_day}&adult=include&count=250'
                self.logger.info(f"Scraping URL: {url}")
                try:
                    driver.get(url)
                    while self.click_show_more(driver):
                        pass
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'li.ipc-metadata-list-summary-item'))
                    )
                    movie_divs = driver.find_elements(By.CSS_SELECTOR, 'li.ipc-metadata-list-summary-item')
                    self.logger.info(f"Found {len(movie_divs)} movie items after fully loading the page.")
                    futures = []
                    for movie_div in movie_divs:
                        movie_data = self.get_movie_data(movie_div)
                        if movie_data and movie_data['imdb_id'] not in self.scraped_imdb_ids:
                            futures.append(self.executor.submit(self.process_movie, movie_data))
                    for future in as_completed(futures):
                        result = future.result()
                        if result:
                            self.scraped_imdb_ids.add(result['imdb_id'])
                            yield result
                    self.scraped_years_months.add((year, month))
                except WebDriverException as e:
                    self.logger.error(f"WebDriverException encountered: {e}")
                except Exception as e:
                    self.logger.error(f"Unexpected error: {e}")
        finally:
            driver.quit()

    def process_movie(self, movie_data):
        if self.is_valid_movie(movie_data):
            tmdb_data = self.fetch_tmdb_data(movie_data)
            if tmdb_data:
                return self.clean_movie_data(tmdb_data, movie_data)
        return None

    def populate_year_month_queue(self, start, end=None):
        if end is None:
            current_year = datetime.now().year
            current_month = datetime.now().month
        else:
            current_year = end
            current_month = 12

        for year in range(start, current_year + 1):
            last_month = current_month if year == current_year else 12

            for month in range(1, last_month + 1):
                self.year_month_queue.put((year, month))

    def get_movie_data(self, movie_div):
        selectors = {
            'title': 'h3.ipc-title__text',
            'year': 'span.dli-title-metadata-item:nth-of-type(1)',
            'movie_url': 'a.ipc-lockup-overlay',
            'imdb_rating': 'span.ipc-rating-star--rating',
            'imdb_votes': 'span.ipc-rating-star--voteCount',
            'metascore': 'span.metacritic-score-box'
        }
        movie_data = {}
        for key, selector in selectors.items():
            try:
                element = movie_div.find_element(By.CSS_SELECTOR, selector)
                if key == 'movie_url':
                    movie_data[key] = element.get_attribute('href')
                elif key == 'imdb_votes':
                    movie_data[key] = self.convert_votes(element.text)
                elif key in ['imdb_rating', 'metascore']:
                    movie_data[key] = self.convert_to_float(element.text)
                else:
                    movie_data[key] = element.text
            except NoSuchElementException:
                movie_data[key] = None
        movie_data['imdb_id'] = movie_data['movie_url'].split('/')[-2] if movie_data.get('movie_url') else None
        return movie_data

    @staticmethod
    def convert_votes(votes_str):
        if not votes_str:
            return None
        votes_str = votes_str.replace('(', '').replace(')', '').replace(',', '').lower()
        if 'k' in votes_str:
            return int(float(votes_str.replace('k', '')) * 1000)
        elif 'm' in votes_str:
            return int(float(votes_str.replace('m', '')) * 1000000)
        return int(votes_str) if votes_str.isdigit() else None

    @staticmethod
    def convert_to_float(value):
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def is_valid_movie(movie_data):
        return movie_data.get('title') and movie_data.get('imdb_id')

    def click_show_more(self, driver):
        try:
            show_more_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.ipc-see-more__button'))
            )
            driver.execute_script("arguments[0].click();", show_more_button)
            time.sleep(1)
            return True
        except (TimeoutException, NoSuchElementException):
            return False

    def fetch_tmdb_data(self, movie_data):
        with ThreadPoolExecutor(max_workers=3) as executor:
            tmdb_id_future = executor.submit(self.get_tmdb_movie_id, movie_data['imdb_id'])
            tmdb_id = tmdb_id_future.result()
            if tmdb_id:
                movie_data_future = executor.submit(self.get_movie_data_tmdb, tmdb_id)
                trailer_future = executor.submit(self.get_trailer_link, tmdb_id)
                tmdb_data = movie_data_future.result()
                trailer_link = trailer_future.result()
                if tmdb_data:
                    tmdb_data['trailer_link'] = trailer_link
                    return tmdb_data
        return None

    def get_tmdb_movie_id(self, imdb_id):
        try:
            tmdb_url = f"{self.base_tmdb_url}/find/{imdb_id}"
            params = {'api_key': self.tmdb_api_key, 'external_source': 'imdb_id'}
            response = self.session.get(tmdb_url, params=params)
            response.raise_for_status()
            data = response.json()
            if data.get('movie_results'):
                return data['movie_results'][0]['id']
            elif data.get('tv_results'):
                return data['tv_results'][0]['id']
        except requests.RequestException as e:
            self.logger.error(f"Error fetching TMDb ID: {e}")
        return None

    def get_movie_data_tmdb(self, tmdb_id):
        try:
            tmdb_url = f"{self.base_tmdb_url}/movie/{tmdb_id}"
            params = {'api_key': self.tmdb_api_key}
            response = self.session.get(tmdb_url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            self.logger.error(f"Error fetching TMDb movie data: {e}")
        return None

    def get_trailer_link(self, tmdb_id):
        try:
            tmdb_url = f"{self.base_tmdb_url}/movie/{tmdb_id}/videos"
            params = {'api_key': self.tmdb_api_key}
            response = self.session.get(tmdb_url, params=params)
            response.raise_for_status()
            video_data = response.json().get('results', [])
            if video_data:
                for video in video_data:
                    if video['type'].lower() == 'trailer':
                        return f"https://www.youtube.com/watch?v={video['key']}"
        except requests.RequestException as e:
            self.logger.error(f"Error fetching TMDb trailer data: {e}")
        return None

    def clean_movie_data(self, tmdb_data, imdb_data):
        cleaned = {
            'title': tmdb_data.get('title', imdb_data.get('title')),
            'original_title': tmdb_data.get('original_title'),
            'imdb_id': tmdb_data.get('imdb_id', imdb_data.get('imdb_id')),
            'tmdb_id': tmdb_data.get('id'),
            'year': imdb_data.get('year'),
            'release_date': tmdb_data.get('release_date'),
            'runtime': tmdb_data.get('runtime'),
            'poster_path': f"https://image.tmdb.org/t/p/original{tmdb_data.get('poster_path', '')}" if tmdb_data.get(
                'poster_path') else None,
            'backdrop_path': f"https://image.tmdb.org/t/p/original{tmdb_data.get('backdrop_path', '')}" if tmdb_data.get(
                'backdrop_path') else None,
            'homepage': tmdb_data.get('homepage'),
            'imdb_rating': imdb_data.get('imdb_rating'),
            'imdb_votes': imdb_data.get('imdb_votes'),
            'imdb_metascore': imdb_data.get('metascore'),
            'tmdb_vote_average': float(tmdb_data.get('vote_average')) if tmdb_data.get(
                'vote_average') is not None else None,
            'tmdb_vote_count': int(tmdb_data.get('vote_count')) if tmdb_data.get('vote_count') is not None else None,
            'genres': [genre['name'] for genre in tmdb_data.get('genres', [])],
            'overview': tmdb_data.get('overview'),
            'tagline': tmdb_data.get('tagline'),
            'budget': tmdb_data.get('budget'),
            'revenue': tmdb_data.get('revenue'),
            'adult': tmdb_data.get('adult'),
            'original_language': tmdb_data.get('original_language'),
            'popularity': float(tmdb_data.get('popularity')) if tmdb_data.get('popularity') is not None else None,
            'status': tmdb_data.get('status'),
            'origin_country': tmdb_data.get('origin_country', []),
            'production_companies': [company['name'] for company in tmdb_data.get('production_companies', [])],
            'production_countries': [country['name'] for country in tmdb_data.get('production_countries', [])],
            'spoken_languages': [lang['english_name'] for lang in tmdb_data.get('spoken_languages', [])],
            'cast': [cast_member['name'] for cast_member in tmdb_data.get('credits', {}).get('cast', [])][:10],
            'crew': [crew_member['name'] for crew_member in tmdb_data.get('credits', {}).get('crew', [])][:10],
            'keywords': [keyword['name'] for keyword in tmdb_data.get('keywords', {}).get('keywords', [])],
            'trailer_link': tmdb_data.get('trailer_link'),
            'scraped_at': datetime.now().isoformat(),
        }
        return cleaned


if __name__ == '__main__':
    process = CrawlerProcess()
    process.crawl(IMDbTMDbSpider, tmdb_api_key="your_tmdb_api_key", num_instances=3, start=1950)
    process.start()
