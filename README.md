# IMDb & TMDb Movie Scraper

[![License: MIT](https://img.shields.io/github/license/WhoIsJayD/IMDB-Scrapper)](https://github.com/WhoIsJayD/IMDB-Scrapper/blob/main/LICENSE.md)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![GitHub issues](https://img.shields.io/github/issues/WhoIsJayD/IMDB-Scrapper)](https://github.com/WhoIsJayD/IMDB-Scrapper/issues)
[![Scrapy](https://img.shields.io/badge/built%20with-Scrapy-green)](https://scrapy.org/)

A powerful Scrapy project designed to efficiently scrape movie and TV series data from IMDb, enriching it with additional details from the TMDb API. This repository offers two distinct spiders: a straightforward **basic scraper** for simple tasks and a high-performance **advanced scraper** for large-scale, concurrent data collection.

## 🌟 Key Features

This project is packed with features to make movie data scraping flexible and powerful.

#### General
- **Dual Source Scraping**: Extracts initial data from IMDb search pages and enriches it with a wealth of information from the TMDb API.
- **Rich Data Collection**: Gathers a wide range of data points including ratings, metadata, posters, cast, crew, and more.
- **Multiple Output Formats**: Automatically saves scraped data into both `movies.json` and `movies.csv` files.
- **Data Cleaning**: Includes logic to process and clean data for consistency.

#### `advance_scrapper.py`
- **High-Concurrency**: Utilizes `ThreadPoolExecutor` to run multiple scraping instances in parallel, dramatically speeding up data collection.
- **Customizable Scraping Range**: Specify the exact date range (`start_year`, `end_year`) for targeted scraping.
- **Robust Error Handling**: Implements a resilient `requests.Session` with automatic retries on failed requests or server errors.
- **Efficient Task Management**: Uses a queue to manage scraping tasks by year and month, ensuring complete and orderly data collection.
- **Dynamic Page Loading**: Leverages Selenium to handle dynamically loaded content and "Show More" pagination on IMDb.
- **Fine-tuned Scrapy Settings**: Comes with optimized settings for performance, throttling, and request management.

#### `basic_scrapper.py`
- **Simplicity**: An easy-to-use spider perfect for smaller scraping tasks or for understanding the core logic.
- **Selenium Integration**: Also uses Selenium to navigate and scrape JavaScript-rendered pages.
- **TMDb Integration**: Fetches additional data from TMDb for each movie found.

## 📂 Project Structure

```plaintext
.
├── imdbscrapper
│   ├── spiders
│   │   ├── advance_scrapper.py  # Advanced, concurrent spider
│   │   ├── basic_scrapper.py    # Simple, sequential spider
│   ├── items.py
│   ├── middlewares.py
│   ├── pipelines.py
│   └── settings.py
├── LICENSE.md
├── README.md
├── requirements.txt
├── scrapy.cfg
└── setup.py
```

## 🛠️ Getting Started

Follow these instructions to get the project up and running on your local machine.

### Prerequisites

- Python 3.10+
- Google Chrome browser installed
- [ChromeDriver](https://googlechromelabs.github.io/chrome-for-testing/) matching your Chrome version

### Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/WhoIsJayD/IMDB-Scrapper.git](https://github.com/WhoIsJayD/IMDB-Scrapper.git)
    cd IMDB-Scrapper
    ```

2.  **Install dependencies:**
    Create a virtual environment (recommended) and install the required packages.
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    pip install -r requirements.txt
    ```

3.  **Set up ChromeDriver:**
    Ensure the ChromeDriver executable is in your system's `PATH`.

4.  **Set up TMDb API Key:**
    You will need an API key from [TMDb](https://www.themoviedb.org/signup). Once you have your key, you can pass it as an argument when running the spider.

## ⚙️ Usage

You can run either the basic or the advanced scraper.

### Basic Scraper
Run the basic scraper to collect a limited set of data from a predefined start URL.
```bash
scrapy crawl basic_scrapper -a tmdb_api_key="YOUR_TMDB_API_KEY"
```

### Advanced Scraper
The advanced scraper is highly recommended for its speed and configurability.
```bash
scrapy crawl advance_scrapper -a tmdb_api_key="YOUR_TMDB_API_KEY" -a start_year=2020 -a end_year=2023 -a num_instances=5
```

#### Configuration Options (`advance_scrapper`)
- **`tmdb_api_key`**: (Required) Your API key for TMDb.
- **`start_year`**: The first year of the release date range to scrape.
- **`end_year`**: The last year of the release date range to scrape.
- **`num_instances`**: The number of concurrent browser instances to run. A higher number leads to faster scraping but consumes more resources.

## 📁 Output Data Schema

The scrapers produce `movies.json` and `movies.csv` files with the following fields:

| Field | Description | Source |
| :--- | :--- | :--- |
| `title` | The movie title. | TMDb / IMDb |
| `original_title`| The original title, if different. | TMDb |
| `imdb_id` | Unique IMDb identifier (e.g., `tt0111161`). | IMDb |
| `tmdb_id` | Unique TMDb identifier. | TMDb |
| `year` | Release year noted on IMDb. | IMDb |
| `release_date`| The full release date (YYYY-MM-DD). | TMDb |
| `runtime` | Movie runtime in minutes. | TMDb |
| `poster_path` | Full URL to the movie poster image. | TMDb |
| `backdrop_path`| Full URL to the backdrop image. | TMDb |
| `homepage` | Link to the movie's official homepage. | TMDb |
| `imdb_rating` | IMDb user rating. | IMDb |
| `imdb_votes` | Number of votes for the IMDb rating. | IMDb |
| `imdb_metascore`| Metacritic score. | IMDb |
| `tmdb_vote_average`| TMDb user rating average. | TMDb |
| `tmdb_vote_count`| Number of votes for the TMDb rating. | TMDb |
| `genres` | List of genres associated with the movie. | TMDb |
| `overview` | A brief plot summary. | TMDb |
| `tagline` | The movie's tagline. | TMDb |
| `budget` | Production budget in USD. | TMDb |
| `revenue` | Worldwide revenue in USD. | TMDb |
| `production_companies` | List of production companies. | TMDb |
| `production_countries` | List of production countries. | TMDb |
| `spoken_languages` | List of spoken languages. | TMDb |
| `cast` | List of the top 10 cast members. | TMDb |
| `crew` | List of top 10 crew members. | TMDb |
| `keywords` | List of keywords associated with the movie. | TMDb |
| `trailer_link`| A YouTube link to the movie trailer. | TMDb |
| `scraped_at` | Timestamp of when the data was scraped. | Scraper |

## ⚠️ Disclaimer

This tool is intended for educational purposes only. Please respect the terms of service of both IMDb and TMDb. Be responsible and avoid overwhelming their servers by keeping scraping rates reasonable.

## 📝 License

This project is licensed under the MIT License. See the [LICENSE.md](LICENSE.md) file for details.

## 📞 Contact

Jaydeep Solanki - [jaydeep.solankee@yahoo.com](mailto:contactjaydeepsolanki@gmail.com)

Project Link: [https://github.com/WhoIsJayD/IMDB-Scrapper](https://github.com/WhoIsJayD/IMDB-Scrapper)

## 🙌 Acknowledgments

- Special thanks to **IMDb** and **TMDb** for providing the data.
- The **Scrapy** and **Selenium** communities for their fantastic tools.
