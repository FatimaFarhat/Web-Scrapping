# Web-Scrapping
Parse a Sitemap, Scrape Articles, Store Data

## Overview

This project is a Python-based web scraper designed to extract articles from almayadeen website's sitemap, parse their metadata, and store them in a structured JSON format. The scraper handles multiple tasks, including fetching sitemap URLs, extracting article URLs, and scraping full article content and metadata. It also includes functionality to save the data in compressed `.json.gz` format for efficient storage.

## Features

- **Sitemap Parsing**: Retrieves a list of monthly sitemaps from the website's sitemap index.
- **Article Scraping**: Extracts metadata and full article text from each article URL found in the sitemap.
- **Handles Arabic Content**: Fixes paragraph order for articles in Arabic by reversing the paragraph sequence.
- **Data Saving**: Saves scraped data in JSON format, with optional gzip compression.
- **Error Handling**: Manages various HTTP and parsing errors gracefully, ensuring robustness.

## Architecture

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

## Installation

1. Clone the repository:
    \`\`\`bash
    git clone https://github.com/your_username/sitemap-article-scraper.git
    \`\`\`
2. Navigate to the project directory:
    \`\`\`bash
    cd sitemap-article-scraper
    \`\`\`
3. Install the dependencies:
    \`\`\`bash
    pip install -r requirements.txt
    \`\`\`

## Usage

To run the scraper, execute the \`main()\` function in the script. This will fetch sitemaps, scrape articles, and save them to a JSON file.

\`\`\`bash
python scraper.py
\`\`\`

You can adjust the maximum number of articles to scrape by changing the \`max_articles\` parameter in the \`main()\` function.

\`\`\`python
max_articles = 5  # Adjust this value to scrape more or fewer articles
\`\`\`

### Customizing Output

- **Save All Articles**: The scraper will save all scraped articles to a \`json.gz\` file if you scrape across multiple months.
- **Saving by Month**: The \`FileUtility\` class can save articles monthly, storing them in compressed \`.json.gz\` files for easy retrieval.

## File Structure

\`\`\`
.
├── scraper.py            # Main scraper script
├── README.md             # Project documentation
├── requirements.txt      # List of dependencies
└── data/                 # Directory where scraped articles are saved
\`\`\`

## Workflow Diagram

\`\`\`mermaid
graph TD
    A[Start] --> B[Fetch Sitemap Index]
    B --> C{Monthly Sitemaps Found?}
    C -->|Yes| D[Fetch Article URLs]
    C -->|No| E[End]
    D --> F[Scrape Article Content & Metadata]
    F --> G{Valid Article?}
    G -->|Yes| H[Save Article Data]
    G -->|No| D
    H --> I{Max Articles Scraped?}
    I -->|Yes| E
    I -->|No| D
\`\`\`

### Sitemap Fetching

- The **SitemapParser** fetches the sitemap index and extracts individual monthly sitemap URLs.
- For each monthly sitemap, it retrieves all article URLs listed.

### Article Scraping

- The **ArticleScraper** fetches the article page and extracts metadata from the embedded JSON inside \`<script>\` tags.
- The full article text is extracted from \`<p>\` tags, with specific handling for Arabic articles to reverse paragraph order.

### Data Saving

- The scraped articles are saved incrementally in compressed \`.json.gz\` format, organized by month and year, or saved all together.

## JSON Data Format

Each article is stored in JSON format with the following structure:

\`\`\`json
{
  "url": "https://example.com/article",
  "post_id": "123456",
  "title": "Sample Article",
  "keywords": ["example", "sample"],
  "thumbnail": "https://example.com/image.jpg",
  "publication_date": "2024-09-05",
  "last_updated_date": "2024-09-05",
  "author": "John Doe",
  "full_article_text": "This is the article content...",
  "video_duration": "3:45",
  "word_count": "500",
  "lang": "en",
  "description": "A brief description of the article"
}
\`\`\`

## Error Handling

- **HTTP Errors**: If the sitemap or an article URL fails to load, the error is logged, and the scraper continues with the next URL.
- **Metadata Parsing Errors**: If JSON metadata parsing fails, the article will be skipped, and the error will be logged.

## Future Improvements

- **Multithreading**: Parallel scraping for faster article retrieval.
- **Advanced Logging**: Implement logging with different verbosity levels for debugging and monitoring.
- **More Languages**: Add support for other languages that may have different scraping needs.

---

### License

This project is licensed under the MIT License

# Write the content to README.md file
with open('README.md', 'w', encoding='utf-8') as f:
    f.write(readme_content)

print("README.md has been generated.")
