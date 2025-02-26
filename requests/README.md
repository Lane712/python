# Douban Web Scraper

This Python script is designed to crawl movie information from Douban (a popular Chinese film and book review website). Below is an overview of its functionality and structure.

## Requirements

- python 3.x
- requests
- BeautifulSoup4
- fake_useragent
- lxml
- re

## Structure

```
 project/
 ├── movie_htmls/
 │   └── [title].html
 ├── 豆瓣电影Top250.html
 ├── 豆瓣电影Top250.json
 ├── hrefs.json
 ├── movies.json
 └── scraper.py
```

## Usage

1. Beginning:
   The script starts by defining HTTP headers and regular expressions to extract specific movie details (e.g., origin and language).

2. HTML Parsing:
   
   - `prettify_html `formats and saves HTML content to local storage.
   
   - `parse_homepage` extracts basic information from Douban's homepage (partially implemented).
   
   - `get_hrefs_from_html` parses movie links from a saved HTML file and saves them into a JSON file.
   
   - `read_hrefs_from_json` reads movie links from a JSON file for further processing.

3. Fetching Pages:
   The `fetch_page` function retrieves HTML content from a target URL using a randomized user agent to mimic browser requests and avoid detection.

4. Detailed Movie Data Extraction:
   The `parse_movie_details` function extracts detailed information from each movie's page, including:

> Title,  Poster URL,  Rating,  Genres,  region,  Languag,  Runtime,  Summary

5. Data Storage:
   
   - Movie links are stored as JSON files.
   
   - Parsed movie details are saved in a structured movies.json file.
   
   - HTML pages for each movie are saved locally under the movie_htmls directory for cache purposes.

## Notes

Rate Limiting: The script includes a 3-second delay between requests to avoid overwhelming the server. Adjust this value if needed.

Error Handling: Basic error handling is implemented, but additional checks may be required for robustness.

Data Accuracy: The script relies on the structure of Douban's HTML. If the website changes, the parsing logic may need updates. 

## Disclaimer

This script is intended for educational purposes only. Web scraping may violate the terms of service of some websites. Always ensure compliance with local laws and website policies before crawling.

---

This script is intended to help you learn and test web scraping techniques. Use it responsibly and ethically.
