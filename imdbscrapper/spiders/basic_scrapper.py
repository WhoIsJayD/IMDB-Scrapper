import requests
import scrapy
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from scrapy.crawler import CrawlerProcess
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class IMDbTMDbSpider(scrapy.Spider):
    name = 'basic_scrapper'
    allowed_domains = ['imdb.com', 'themoviedb.org']
    start_urls = [
        'https://www.imdb.com/search/title/?title_type=feature,tv_series&release_date=2003-01-01,2003-01-31&adult=include&count=250'
    ]

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'DOWNLOAD_DELAY': 1,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'FEEDS': {
            'movies.json': {'format': 'json', 'overwrite': False},
            'movies.csv': {'format': 'csv', 'overwrite': False},
        },
    }

    def __init__(self, max_movies=300000, tmdb_api_key="your_tmdb_api_key", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_movies = int(max_movies)
        self.movie_count = 0
        self.tmdb_api_key = tmdb_api_key
        self.driver = webdriver.Chrome()
        self.base_tmdb_url = "https://api.themoviedb.org/3"
        self.executor = ThreadPoolExecutor(max_workers=5)

    def parse(self, response):
        self.driver.get(response.url)

        while self.movie_count < self.max_movies:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.sc-59c7dc1-3'))
            )

            movie_divs = self.driver.find_elements(By.CSS_SELECTOR, 'div.sc-59c7dc1-3')
            futures = []

            for movie_div in movie_divs:
                if self.movie_count >= self.max_movies:
                    break

                movie_data = self.get_movie_data(movie_div)
                if movie_data and self.is_valid_movie(movie_data):
                    self.movie_count += 1
                    futures.append(self.executor.submit(self.fetch_tmdb_data, movie_data))

            for future in as_completed(futures):
                result = future.result()
                if result:
                    yield result

            if not self.click_show_more():
                break

        self.driver.quit()

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
                if key == 'movie_url':
                    movie_data[key] = movie_div.find_element(By.CSS_SELECTOR, selector).get_attribute('href')
                elif key == 'imdb_votes':
                    votes = movie_div.find_element(By.CSS_SELECTOR, selector).text
                    movie_data[key] = self.convert_votes(votes)
                elif key in ['imdb_rating', 'metascore']:
                    value = movie_div.find_element(By.CSS_SELECTOR, selector).text
                    movie_data[key] = self.convert_to_float(value)
                else:
                    movie_data[key] = movie_div.find_element(By.CSS_SELECTOR, selector).text
            except NoSuchElementException:
                movie_data[key] = None

        movie_data['imdb_id'] = movie_data['movie_url'].split('/')[-2]

        return movie_data

    def convert_votes(self, votes_str):
        votes_str = votes_str.replace('(', '').replace(')', '').replace(',', '').lower()
        if 'k' in votes_str:
            return int(float(votes_str.replace('k', '')) * 1000)
        elif 'm' in votes_str:
            return int(float(votes_str.replace('m', '')) * 1000000)
        else:
            return int(votes_str) if votes_str.isdigit() else None

    def convert_to_float(self, value):
        try:
            return float(value)
        except ValueError:
            return None

    def is_valid_movie(self, movie_data):
        return movie_data['title'] is not None and movie_data['imdb_id'] is not None

    def click_show_more(self):
        try:
            show_more_button = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.ipc-see-more__button'))
            )
            self.driver.execute_script("arguments[0].click();", show_more_button)
            time.sleep(2)
            return True
        except (TimeoutException, NoSuchElementException):
            return False

    def fetch_tmdb_data(self, movie_data):
        tmdb_id = self.get_tmdb_movie_id(movie_data['imdb_id'])
        if tmdb_id:
            tmdb_data = self.get_movie_data_tmdb(tmdb_id)
            trailer_link = self.get_trailer_link(tmdb_id)
            if tmdb_data:
                return self.clean_movie_data(tmdb_data, movie_data, trailer_link)
        return None

    def get_tmdb_movie_id(self, imdb_id):
        url = f"{self.base_tmdb_url}/find/{imdb_id}?api_key={self.tmdb_api_key}&external_source=imdb_id"
        response = self.make_api_request(url)
        if response and response.get('movie_results'):
            return response['movie_results'][0]['id']
        return None

    def get_movie_data_tmdb(self, tmdb_id):
        url = f"{self.base_tmdb_url}/movie/{tmdb_id}?api_key={self.tmdb_api_key}&append_to_response=credits,keywords"
        return self.make_api_request(url)

    def get_trailer_link(self, tmdb_id):
        url = f"{self.base_tmdb_url}/movie/{tmdb_id}/videos?api_key={self.tmdb_api_key}"
        response = self.make_api_request(url)
        if response and response.get('results'):
            for video in response['results']:
                if video['type'] == 'Trailer' and video['site'] == 'YouTube':
                    return f"https://www.youtube.com/watch?v={video['key']}"
        return None

    def make_api_request(self, url):
        for _ in range(5):
            try:
                response = requests.get(url)
                if response.status_code == 429:
                    time.sleep(5)
                    continue
                response.raise_for_status()
                return response.json()
            except requests.RequestException as e:
                self.logger.error(f"API request failed: {e}")
                return None

    def clean_movie_data(self, tmdb_data, imdb_data, trailer_link):
        imdb_title = imdb_data.get('title')
        imdb_year = imdb_data.get('year')
        imdb_id = tmdb_data.get('imdb_id', imdb_data.get('imdb_id'))
        tmdb_id = tmdb_data.get('id')

        imdb_rating = imdb_data.get('imdb_rating')
        imdb_votes = imdb_data.get('imdb_votes')
        imdb_metascore = imdb_data.get('metascore')
        tmdb_vote_average = float(tmdb_data.get('vote_average'))
        tmdb_vote_count = int(tmdb_data.get('vote_count'))

        poster_url = f"https://image.tmdb.org/t/p/original{tmdb_data.get('poster_path', '')}"
        backdrop_url = f"https://image.tmdb.org/t/p/original{tmdb_data.get('backdrop_path', '')}"
        homepage = tmdb_data.get('homepage')

        production_companies = list({company['name'] for company in tmdb_data.get('production_companies')})
        production_countries = list({country['name'] for country in tmdb_data.get('production_countries')})
        spoken_languages = list({lang['english_name'] for lang in tmdb_data.get('spoken_languages')})
        origin_country = [origin for origin in tmdb_data.get('origin_country')]

        cast = [cast_member['name'] for cast_member in tmdb_data.get('credits').get('cast')][:10]
        crew = [crew_member['name'] for crew_member in tmdb_data.get('credits').get('crew')][:10]

        keywords = [keyword['name'] for keyword in tmdb_data.get('keywords', {}).get('keywords')]

        cleaned = {
            'title': tmdb_data.get('title', imdb_title),
            'original_title': tmdb_data.get('original_title'),
            'imdb_id': imdb_id,
            'tmdb_id': tmdb_id,
            'year': imdb_year,
            'release_date': tmdb_data.get('release_date'),
            'runtime': tmdb_data.get('runtime'),
            'poster_path': poster_url,
            'backdrop_path': backdrop_url,
            'homepage': homepage,
            'imdb_rating': imdb_rating,
            'imdb_votes': imdb_votes,
            'imdb_metascore': imdb_metascore,
            'tmdb_vote_average': tmdb_vote_average,
            'tmdb_vote_count': tmdb_vote_count,
            'genres': [genre['name'] for genre in tmdb_data.get('genres')],
            'overview': tmdb_data.get('overview'),
            'tagline': tmdb_data.get('tagline'),
            'budget': tmdb_data.get('budget'),
            'revenue': tmdb_data.get('revenue'),
            'adult': tmdb_data.get('adult'),
            'original_language': tmdb_data.get('original_language'),
            'popularity': float(tmdb_data.get('popularity')),
            'status': tmdb_data.get('status'),
            'origin_country': origin_country,
            'production_companies': production_companies,
            'production_countries': production_countries,
            'spoken_languages': spoken_languages,
            'cast': cast,
            'crew': crew,
            'keywords': keywords,
            'trailer_link': trailer_link,
        }

        return cleaned

if __name__ == '__main__':
    process = CrawlerProcess()
    process.crawl(IMDbTMDbSpider, max_movies=5, tmdb_api_key="your_tmdb_api_key")
    process.start()
