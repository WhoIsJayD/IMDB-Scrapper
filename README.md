# IMDb Scraper

This project contains two Scrapy spiders for scraping movie data from IMDb and TMDb: a basic scraper and an advanced scraper with additional features.

## Project Structure

```
.
├── imdbscrapper
│   ├── spiders
│   │   ├── __init__.py
│   │   ├── advance_scrapper.py
│   │   ├── basic_scrapper.py
│   ├── __init__.py
│   ├── items.py
│   ├── middlewares.py
│   ├── pipelines.py
│   └── settings.py
│ 
├── LICENSE.md
├── README.md
├── requirements.txt
├── scrapy.cfg
└── setup.py
```

## Features

### Basic Scraper (`basic_scrapper.py`)
- Scrapes movie data from IMDb search pages
- Fetches additional data from TMDb API
- Supports pagination through "Show More" button
- Saves data in JSON and CSV formats

### Advanced Scraper (`advance_scrapper.py`)
- All features of the basic scraper
- Multi-threaded scraping for improved performance
- More robust error handling and retries
- Extended data fields and cleaning

## Requirements

- Python 3.7+
- Scrapy
- Selenium
- requests
- concurrent.futures

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/WhoIsJayD/imdb-scraper.git
   cd imdb-scraper
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up your TMDb API key in the spider files.

## Usage

### Basic Scraper

Run the basic scraper with:

```
scrapy crawl basic_scrapper
```

### Advanced Scraper

Run the advanced scraper with:

```
scrapy crawl advance_scrapper
```

## Configuration

- Adjust the `max_movies` parameter in `basic_scrapper.py` to control the number of movies to scrape.
- Modify the `start year`, `end year`, and `num_instances` parameters in `advance_scrapper.py` to customize the scraping range and concurrency.

## Output

The scrapers will generate two output files:
- `movies.json`: Contains the scraped data in JSON format
- `movies.csv`: Contains the scraped data in CSV format

## Customization

- Modify the `custom_settings` in each spider to adjust scraping behavior.
- Edit the `clean_movie_data` method to customize the data cleaning process.

## Notes

- Ensure you comply with IMDb and TMDb terms of service when using these scrapers.
- Be mindful of rate limiting and consider implementing appropriate delays between requests.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Contact

For any inquiries or permissions, please contact:

- **Name**: Jaydeep Solanki
- **Email**: jaydeep.solankee@yahoo.com
- **LinkedIn**: www.linkedin.com/in/solanki-jaydeep

## Acknowledgments

- IMDb for providing the movie data
- TMDb for their comprehensive API
- Scrapy and Selenium communities for their excellent tools and documentation