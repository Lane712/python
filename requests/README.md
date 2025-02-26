# Douban Web Scraper

This script is designed to scrape movie and book information from the Douban website. It extracts details such as titles, ratings, genres, and summaries, and stores them in JSON format.

## Features
- Extracts movie and book data from Douban.
- Handles pagination and multiple pages.
- Uses BeautifulSoup for HTML parsing and fake_useragent for random User-Agent headers.
- Saves extracted data in JSON format.

## Requirements
- Python 3.x
- Requests
- BeautifulSoup4
- fake_useragent
- lxml

## Installation
1. Clone this repository.
2. Install the required packages using pip:
  ```bash
  pip install requests beautifulsoup4 fake_useragent lxml
  ```

## Usage
1. Run the script using:
  ```bash
  python requests_get.py
  ```
2. The script will scrape movie data from Douban and save it to doubanMovieTop250.json .

## Functions
#### `index_soup()`  
Scrapes the main page of Douban for movie and book information.<br>
#### `get_hrefs()`  
Extracts all sub-links from a given HTML file.<br>
#### `movie_soup(html)`  
Parses movie details from a given HTML content.<br>
#### `main()`  
Main function to orchestrate scraping and data saving.<br>

## Output
The script will generate a JSON file (`doubanMovieTop250.json`) containing movie data, including:
>Title, Rating, Genre, Origin, Language, Runtime, Summary.

## Disclaimer  
This script is intended solely for testing and educational purposes. The primary goal is to facilitate learning about web scraping techniques, data extraction, and Python programming. The following points must be noted:

### 1. Educational Use Only:
This script is designed to help users understand the basics of web scraping and data processing. It is not intended for commercial use or any other unauthorized purposes.<br>

### 2. Respect Website Policies:
Always review and adhere to the website's terms of service and robots.txt file. This script should not be used to scrape data from websites that explicitly prohibit web scraping.<br>

### 3. Responsible Usage:
When using this script, ensure that your actions do not place undue stress on the website's servers. The script includes delays to minimize impact, but users should avoid excessive or rapid requests.<br>

### 4. Data Handling:
Any data extracted using this script should be used responsibly and ethically. It is intended for learning and testing purposes only and should not be distributed or used for commercial gain without permission from the website owner.<br>

### 5. No Guarantee of Functionality:
This script is provided as-is without any warranty. The website's structure may change over time, and the script may need to be updated accordingly.<br>

### 6. Legal and Ethical Considerations:
By using this script, you acknowledge that you are responsible for your actions and that you will comply with all applicable laws and regulations. The author of this script is not liable for any misuse or unintended consequences resulting from its use.<br>

---

This script is intended to help you learn and test web scraping techniques. Use it responsibly and ethically.
