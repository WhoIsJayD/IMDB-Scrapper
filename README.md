# IMDb & TMDb Movie Scraper

[![License: MIT](https://img.shields.io/github/license/WhoIsJayD/IMDB-Scrapper)](https://github.com/WhoIsJayD/IMDB-Scrapper/blob/main/LICENSE.md)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![GitHub Issues](https://img.shields.io/github/issues/WhoIsJayD/IMDB-Scrapper)](https://github.com/WhoIsJayD/IMDB-Scrapper/issues)
[![Scrapy](https://img.shields.io/badge/built%20with-Scrapy-green)](https://scrapy.org/)
![Visitor Badge](https://visitor-badge.laobi.icu/badge?page_id=https://github.com/WhoIsJayD/IMDB-Scrapper)

A robust Scrapy-based tool for scraping movie and TV series data from IMDb, enriched with detailed metadata from the TMDb API. This project provides two spiders: a **basic scraper** for small-scale tasks and an **advanced scraper** optimized for high-performance, concurrent data collection.

## 🌟 Features

### Core Functionality
- **Dual-Source Data**: Scrapes IMDb for initial movie data and enhances it with rich metadata from the TMDb API.
- **Comprehensive Data**: Collects titles, ratings, genres, cast, crew, posters, budgets, and more.
- **Flexible Outputs**: Exports data to `movies.json` and `movies.csv` formats.
- **Data Cleaning**: Ensures consistent and reliable data through built-in processing logic.

### Advanced Scraper (`advance_scrapper.py`)
- **High Concurrency**: Uses `ThreadPoolExecutor` for parallel scraping, boosting performance.
- **Customizable Range**: Targets specific release years (`start_year`, `end_year`).
- **Robust Error Handling**: Employs `requests.Session` with automatic retries for stability.
- **Task Management**: Organizes scraping by year/month using a queue for efficiency.
- **Dynamic Content**: Handles JavaScript-rendered pages and pagination with Selenium.
- **Optimized Settings**: Fine-tuned Scrapy configurations for throttling and performance.

### Basic Scraper (`basic_scrapper.py`)
- **User-Friendly**: Ideal for small-scale scraping or learning the project's logic.
- **Selenium Support**: Navigates dynamic IMDb pages with ease.
- **TMDb Enrichment**: Fetches additional metadata for each scraped movie.

## 📂 Project Structure

```plaintext
├── imdbscrapper
│   ├── spiders
│   │   ├── advance_scrapper.py  # High-performance spider
│   │   ├── basic_scrapper.py    # Simple spider
│   ├── items.py                 # Data models
│   ├── middlewares.py           # Custom middleware
│   ├── pipelines.py             # Data processing pipeline
│   └── settings.py              # Scrapy configurations
├── LICENSE.md
├── README.md
├── requirements.txt
├── scrapy.cfg
└── setup.py
```

## 🛠️ Getting Started

### Prerequisites
- Python 3.10+
- Google Chrome browser
- [ChromeDriver](https://googlechromelabs.github.io/chrome-for-testing/) (matching your Chrome version)
- TMDb API key ([sign up here](https://www.themoviedb.org/signup))

### Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/WhoIsJayD/IMDB-Scrapper.git
   cd IMDB-Scrapper
   ```

2. **Set Up a Virtual Environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure ChromeDriver**:
   Ensure ChromeDriver is installed and added to your system's `PATH`.

5. **Obtain TMDb API Key**:
   Register on TMDb to get your API key, which is required for running the spiders.

## ⚙️ Usage

### Running the Basic Scraper
For small-scale scraping tasks:
```bash
scrapy crawl basic_scrapper -a tmdb_api_key="YOUR_TMDB_API_KEY"
```

### Running the Advanced Scraper
For large-scale, high-performance scraping:
```bash
scrapy crawl advance_scrapper -a tmdb_api_key="YOUR_TMDB_API_KEY" -a start_year=2020 -a end_year=2023 -a num_instances=5
```

#### Advanced Scraper Options
- `-a tmdb_api_key`: Your TMDb API key (required).
- `-a start_year`: Starting release year (e.g., 2020).
- `-a end_year`: Ending release year (e.g., 2023).
- `-a num_instances`: Number of concurrent browser instances (default: 5; adjust based on system resources).

## 📁 Output Data Schema

The scraped data is saved in `movies.json` and `movies.csv` with the following fields:

| Field                  | Description                              | Source    |
|------------------------|------------------------------------------|-----------|
| `title`                | Movie title                              | IMDb/TMDb |
| `original_title`       | Original title (if different)            | TMDb      |
| `imdb_id`              | IMDb ID (e.g., `tt0111161`)              | IMDb      |
| `tmdb_id`              | TMDb ID                                  | TMDb      |
| `year`                 | Release year                             | IMDb      |
| `release_date`         | Full release date (YYYY-MM-DD)           | TMDb      |
| `runtime`              | Runtime in minutes                       | TMDb      |
| `poster_path`          | URL to poster image                      | TMDb      |
| `backdrop_path`        | URL to backdrop image                    | TMDb      |
| `homepage`             | Official website URL                     | TMDb      |
| `imdb_rating`          | IMDb user rating                         | IMDb      |
| `imdb_votes`           | Number of IMDb votes                     | IMDb      |
| `imdb_metascore`       | Metacritic score                         | IMDb      |
| `tmdb_vote_average`    | TMDb average rating                      | TMDb      |
| `tmdb_vote_count`      | Number of TMDb votes                     | TMDb      |
| `genres`               | List of genres                           | TMDb      |
| `overview`             | Plot summary                             | TMDb      |
| `tagline`              | Movie tagline                            | TMDb      |
| `budget`               | Production budget (USD)                  | TMDb      |
| `revenue`              | Worldwide revenue (USD)                  | TMDb      |
| `production_companies` | List of production companies             | TMDb      |
| `production_countries` | List of production countries             | TMDb      |
| `spoken_languages`     | List of spoken languages                 | TMDb      |
| `cast`                 | Top 10 cast members                      | TMDb      |
| `crew`                 | Top 10 crew members                      | TMDb      |
| `keywords`             | List of keywords                         | TMDb      |
| `trailer_link`         | YouTube trailer URL                      | TMDb      |
| `scraped_at`           | Timestamp of data collection             | Scraper   |

## 🛠️ Troubleshooting

- **ChromeDriver Issues**: Ensure ChromeDriver matches your Chrome browser version. Check the [Chrome for Testing](https://googlechromelabs.github.io/chrome-for-testing/) page for compatible versions.
- **TMDb API Errors**: Verify your API key and ensure you haven't exceeded TMDb's rate limits.
- **Performance Issues**: Reduce `num_instances` in the advanced scraper if your system struggles with high concurrency.
- **Missing Data**: Check IMDb and TMDb pages manually to confirm data availability, as some fields may be absent.

## 🤝 Contributing

Contributions are welcome! To contribute:
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/your-feature`).
3. Commit your changes (`git commit -m "Add your feature"`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a pull request.

Please report issues or suggest improvements via the [GitHub Issues](https://github.com/WhoIsJayD/IMDB-Scrapper/issues) page.

## ⚠️ Disclaimer

This tool is for **educational purposes only**. Respect IMDb and TMDb's terms of service, and avoid excessive scraping that could overload their servers. Use reasonable request rates and comply with all applicable laws.

## 📝 License

Licensed under the [MIT License](LICENSE.md).

## 📞 Contact

- **Author**: Jaydeep Solanki
- **Email**: [jaydeep.solankee@yahoo.com](mailto:jaydeep.solankee@yahoo.com)
- **Project**: [https://github.com/WhoIsJayD/IMDB-Scrapper](https://github.com/WhoIsJayD/IMDB-Scrapper)

## 🙌 Acknowledgments

- **IMDb** and **TMDb** for providing valuable data.
- **Scrapy** and **Selenium** communities for their powerful tools.
