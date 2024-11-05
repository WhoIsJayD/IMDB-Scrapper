# IMDb-TMDb Scraper

[![License](https://img.shields.io/github/license/WhoIsJayD/IMDB-Scrapper)](https://github.com/WhoIsJayD/IMDB-Scrapper/blob/main/LICENSE.md)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/release/python-310/)
[![Issues](https://img.shields.io/github/issues/WhoIsJayD/IMDB-Scrapper)](https://github.com/WhoIsJayD/IMDB-Scrapper/issues)

This project provides two Scrapy spiders for scraping movie data from **IMDb** and **TMDb**: a **basic scraper** and an **advanced scraper** with additional capabilities for concurrent and customizable scraping.

## 📂 Project Structure

```plaintext
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

## 🚀 Features

### Basic Scraper (`basic_scrapper.py`)
- **IMDb Search Pages**: Scrapes movie details from IMDb search pages.
- **TMDb Integration**: Fetches additional data, such as posters and ratings, using the TMDb API.
- **Pagination**: Supports pagination through the IMDb search "Show More" option.
- **Output**: Saves scraped data as JSON and CSV files.

### Advanced Scraper (`advance_scrapper.py`)
- **Enhanced Features**: Includes all functionalities of the basic scraper.
- **Multi-threaded Scraping**: Utilizes concurrent scraping for faster data collection.
- **Robust Error Handling**: Implements improved retry and error management.
- **Data Enrichment**: Collects extended movie metadata and applies data cleaning.

## 📋 Requirements

- **Python** 3.10+
- **Scrapy**
- **Selenium** (for JavaScript-heavy pages)
- **Requests** (for TMDb API requests)
- **Concurrent Futures** (for parallel scraping)

Install dependencies with:
```bash
pip install -r requirements.txt
```

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/WhoIsJayD/IMDB-Scrapper
   cd IMDB-Scrapper
   ```

2. **Set up API Key**:
   Add your TMDb API key in each spider file or pass it as an argument.

3. **Set up Selenium** (for advanced scraping):
   - Download [ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver/downloads) compatible with your Chrome version.
   - Add ChromeDriver to your system's PATH.

## ⚙️ Usage

### Basic Scraper

Run the basic scraper with:
```bash
scrapy crawl basic_scrapper
```

### Advanced Scraper

Run the advanced scraper with custom parameters:
```bash
scrapy crawl advance_scrapper -a tmdb_api_key="your_tmdb_api_key" -a start_year=2000 -a end_year=2023 -a num_instances=5
```

### Configuration Options

- **`start_year`**: Start year for the movie range.
- **`end_year`**: End year for the movie range.
- **`num_instances`**: Number of concurrent scraping instances.

## 📁 Output

The scrapers produce the following files:
- **movies.json**: Contains movie data in JSON format.
- **movies.csv**: Contains movie data in CSV format.

## 🔧 Customization

- Modify `custom_settings` in each spider to configure scraping behavior.
- Adjust the `clean_movie_data` method in `advance_scrapper.py` to customize data cleaning.

## ⚠️ Notes

- **Legal Compliance**: Ensure your usage complies with IMDb and TMDb terms of service.
- **Rate Limiting**: To avoid blocking, set appropriate delays or intervals.

## 📝 License

This project is licensed under the MIT License. See the [LICENSE.md](LICENSE.md) file for details.

## 📞 Contact

For any inquiries, please reach out:

- **Name**: Jaydeep Solanki
- **Email**: jaydeep.solankee@yahoo.com
- **LinkedIn**: [LinkedIn Profile](https://www.linkedin.com/in/solanki-jaydeep)

## 🙌 Acknowledgments

Special thanks to:
- **IMDb** for the movie data.
- **TMDb** for their API resources.
- The **Scrapy** and **Selenium** communities for their robust tools and documentation.
