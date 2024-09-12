# Article Management API

## Project Overview

This project is a Python-based web scraper designed to extract articles from almayadeen website's sitemap, parse their metadata, and store them in a structured JSON format. The scraper handles multiple tasks, including fetching sitemap URLs, extracting article URLs, and scraping full article content and metadata. It also includes functionality to save the data in compressed `.json.gz` format for efficient storage.
and provides an API for managing and querying articles stored in a MongoDB collection. The API is built with Flask and allows users to filter, count, and analyze articles based on various criteria such as publication dates, word counts, video durations, keywords, and more.

## Table of Contents

1. [Project Overview](#project-overview)
2. [Setup Instructions](#setup-instructions)
3. [Dependencies](#dependencies)
4. [Usage Instructions](#usage-instructions)
5. [Web Scraping](#web-scraping)
6. [API Endpoints](#api-endpoints)
7. [Data Storage](#data-storage)
8. [Scripts Overview](#scripts-overview)

## Setup Instructions

To set up this project locally, follow these steps:

1. **Clone the repository:**

    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2. **Create and activate a virtual environment:**

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3. **Install the dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Run the Flask app:**

    ```bash
    flask run
    ```

## Dependencies

- Python 3.7+
- Flask
- PyMongo
- MongoDB
- Other dependencies specified in the `requirements.txt` file

## Usage Instructions

To use the API, follow the setup instructions to get the project running locally. You can interact with the API using tools like Postman, Curl, or directly from your web browser.

## Web Scraping

This section explains how articles are scraped and stored.

1. **Scraping Setup**: Articles are scraped using Python scripts with libraries such as BeautifulSoup for HTML parsing and Requests for making HTTP calls.
2. **Processing**: Scraped articles are processed to remove unwanted HTML tags and formatted before being stored in MongoDB.
3. **Storing Data**: The scraper will save all scraped articles to a \`json.gz\` file if you scrape across multiple months.then will be stored in  MongoDB, and the script ensures that only relevant fields are kept for querying and analysis.
4. **Architecture**:The web-scraper pythom script consists of the following key components:
 
   The project consists of the following key components:

   1. **\`SitemapParser\`**: 
      - Parses the sitemap index to get URLs of monthly sitemaps.
      - Extracts article URLs from each monthly sitemap.

   2. **\`ArticleScraper\`**: 
      - Fetches the article content and metadata.
      - Removes unwanted HTML elements and extracts the article's full text.
      - Fixes Arabic language article ordering issues.

   3. **\`FileUtility\`**: 
      - Saves the scraped articles in JSON format, optionally compressed.
   
   4. **\`Article\`**: 
      - A data class that encapsulates article metadata and content for easy storage and access.


## API Endpoints

1. **GET /articles_with_video**  
   Description: Retrieves a list of articles that contain a video.  
   Returns: A JSON array of articles with their titles, video durations, and Object IDs.

2. **GET /articles_by_year/<int:year>**  
   Description: Retrieves the number of articles published in a specified year.  
   Parameters: `year` (The year to filter the articles by).  
   Returns: A JSON object with the count of articles published in the specified year.

3. **GET /longest_articles**  
   Description: Retrieves the top 10 articles with the highest word count.  
   Returns: A JSON array of articles with their titles and word counts.

4. **GET /shortest_articles**  
   Description: Retrieves the top 10 articles with the lowest word count.  
   Returns: A JSON array of articles with their titles and word counts.

5. **GET /articles_by_keyword_count**  
   Description: Retrieves the number of articles grouped by the number of keywords they contain.  
   Returns: A JSON array where each entry includes the number of keywords and the count of articles with that many keywords.

6. **GET /articles_with_thumbnail**  
   Description: Retrieves a list of articles that have a thumbnail image.  
   Returns: A JSON array of article titles.

7. **GET /articles_updated_after_publication**  
   Description: Retrieves a list of articles where the `last_updated_date` is after the `publication_date`.  
   Returns: A JSON array of articles with their titles.

8. **GET /articles_by_coverage/<coverage>**  
   Description: Retrieves a list of articles under a specific coverage category.  
   Parameters: `coverage` (The specific coverage value to filter by).  
   Returns: A JSON array of article titles.

9. **GET /popular_keywords_last_X_days/<int:days>**  
   Description: Retrieves the most popular keywords from articles published within the last X days.  
   Parameters: `days` (The number of days to look back).  
   Returns: A JSON array of popular keywords and their counts.

10. **GET /articles_by_month/<int:year>/<int:month>**  
    Description: Retrieves the number of articles published in a specific month of a given year.  
    Parameters: `year` (The year to filter by), `month` (The month to filter by).  
    Returns: A JSON object with the count of articles for the given month and year.

11. **GET /articles_by_word_count_range/<int:min_word_count>/<int:max_word_count>**  
    Description: Retrieves the count of articles within a specified word count range.  
    Parameters: `min_word_count` (Minimum word count), `max_word_count` (Maximum word count).  
    Returns: A JSON object with the count of articles that fall within the given word count range.

12. **GET /articles_with_specific_keyword_count/<int:count>**  
    Description: Retrieves articles that contain exactly the specified number of keywords.  
    Parameters: `count` (The number of keywords to filter by).  
    Returns: A JSON object with the count of articles that have the specified keyword count.

13. **GET /articles_by_specific_date/<date>**  
    Description: Retrieves articles published on a specific date (YYYY-MM-DD format).  
    Returns: A JSON object with the date, article count, and a list of articles.  
    Error Responses:  
      - `400`: Invalid date format.  
      - `404`: No articles found for the given date.

14. **GET /articles_containing_text/<text>**  
    Description: Retrieves articles that contain specific text in their content (case-insensitive).  
    Returns: A JSON object with the text, article count, and a list of articles.  
    Error Responses:  
      - `404`: No articles found containing the specified text.  
      - `500`: Server error.

15. **GET /articles_with_more_than/<int:word_count>**
    - Description: Retrieves articles where the word count exceeds a specified value.
    - Returns: A JSON object with the word count, article count, and a list of articles.
    - Error Responses:
      - `404`: No articles found with more than the specified number of words.
      - `500`: Server error.

16. **GET /articles_grouped_by_coverage**
    - Description: Retrieves the count of articles grouped by the "coverage" category derived from the classes field.
    - Returns: A JSON array with coverage categories and their counts.
    - Error Responses:
      - `500`: Server error.

17. **GET /articles_last_X_hours/<int:hours>**
    - Description: Retrieves articles published in the last X hours.
    - Returns: A JSON array of articles with their titles and publication dates.
    - Error Responses:
      - `404`: No articles found published in the last X hours.
      - `500`: Server error.

18. **GET /articles_by_title_length**
    - Description: Retrieves the number of articles grouped by the length of their titles.
    - Returns: A JSON array with title lengths and their counts.
    - Error Responses:
      - `500`: Server error.

19. **GET /most_updated_articles**
    - Description: Retrieves the top 10 articles that have been updated the most times.
    - Returns: A JSON array of articles with their titles and update counts.
    - Error Responses:
      - `500`: Server error.
     
20. **GET /popular_keywords_last_X_days/<int:days>**
    - Description: Retrieves most popular keywords used in articles published in the last X days.
    - Returns: A JSON object with keywords and their counts.
    - Error Responses:
      - `500`: Server error.
      - Error fetching popular keywords
21. **GET /articles_by_month/<int:year>/<int:month>**
    - Description: Retrieves the number of articles publieshed in a specific month and year. Articles are grouped by month and year
    - Returns: A JSON object with the count of articles.
    - Error Responses:
      - `500`: Server error.
      - Error fetching articles by month
 22. **GET /articles_by_word_count_range/<int:min_word_count>/<int:max_word_count>**
    - Description: Retrieve articles with a word count within a specific range.
    - Returns: A JSON object with the count of articles for the given word count rang.
    - Error Responses:
      - `500`: Server error.
      - Error fetching articles by word count range
 23. **GET /articles_with_specific_keyword_count/<int:count>**
    - Description: Retrieve articles that contain exatly a specific number of keywords.
    - Returns: A JSON object with the count of articles for the given keyword count.
    - Error Responses:
      - `500`: Server error.
      - Error fetching articles with specific keyword count.

 24. **GET /articles_by_specific_date/<date>**
   - Description: Retrieve articles published on a specific date where the date should be             provided in the format 'YYYY-MM-DD'.
   - Returns: A JSON object with the count of articles published in that date.
   - Error Responses:
      - `500`: Server error.
      - Error fetching articles with specific keyword count.

   25. **GET /articles_containing_text/<text>**
      - Description: Retrieve articles that contain a specific text in their content.
       The text will be searched within the 'full_article_text' field
      - Returns: A JSON object with the count of articles contain that text.
      - Error Responses:
         - `500`: Server error.
         - Error fetching articles with specific text.

   26. **GET /articles_with_more_than/<int:word_count>**
      - Description: Retrieve articles with more than a specified number of words.
      - Returns: A JSON object with the count of articles found.
      - Error Responses:
         - `500`: Server error.
         - Error fetching articles with the more than the specified word count.

   27. **GET /articles_grouped_by_coverage**
   - Description: Retrieve the number of articles grouped by their coverage category.
         The 'coverage' category is derived from the 'classes' field of each article.
   - Returns: A JSON object with each coverage category and the count of articles in that category.
   - Error Responses:
     - `500`: Server error.
      - Error fetching articles grouped by coverage.

   28. **GET /articles_last_X_hours/<int:hours>**
       - Description: Retrieve a list of articles published in the last X hours.
      - Returns: A JSON array of articles that were published in the last X hours
      - Error Responses:
         - Error fetching articles grouped by coverage.
        
   29. **GET /articles_by_title_length**
       - Description: Retrieve the number of articles grouped by the length of their title.
      - Returns: A JSON object with the length of title and count of articles having that length.
      - Error Responses:
         - Error fetching articles with specific title length.
        
   30. **GET /most_updated_articles**
       - Description: Retrieve the top 10 articles that have been updated the most times..
      - Returns: A JSON array of articles with their titles and update counts.
      - Error Responses:
         - Error fetching most updated articles.
        
 
    

    



## Data Storage

### `data_storage.py`

The `data_storage.py` script is responsible for loading article data from a JSON file and inserting it into the MongoDB collection. This script assumes that MongoDB is already running and the collection is correctly initialized.

#### Script Overview

- **Imports**: The script uses `pymongo` for interacting with MongoDB and `json` for reading the JSON data.
- **Connection**: Connects to MongoDB using the local instance at `localhost:27017`, and selects the `almayadeen` database and `articles` collection.
- **File Path**: Defines the path to the JSON file that contains the article data.
- **Data Insertion**: Reads the JSON file and inserts its contents into the MongoDB collection.

#### How to Use

1. **Ensure MongoDB is Running**: Make sure your MongoDB server is up and running.
2. **Set File Path**: Verify the `file_path` variable in the script points to your JSON file.
3. **Run the Script**:

    ```bash
    python data_storage.py
    ```

   This will load the data from the specified JSON file and insert it into the `articles` collection in MongoDB.

#### Example Script

```python
import pymongo
import json

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["almayadeen"]
collection = db["articles"]

file_path = 'data//all_articles_original_20K.json'

# Load and insert JSON data
with open(file_path, 'rt', encoding='utf-8') as f:
    data = json.load(f)
    collection.insert_many(data)

print("Data inserted successfully!")
