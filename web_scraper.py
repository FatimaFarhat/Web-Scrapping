from importlib.metadata import metadata
from types import NoneType

import requests
from bs4 import BeautifulSoup
import json
import os
from dataclasses import dataclass
from typing import List, Optional, Dict
import csv
import gzip
from urllib.parse import quote



@dataclass
class Article:

    # Attributes:

    url: str
    post_id: Optional[str]
    title: Optional[str]
    keywords: Optional[List[str]]
    thumbnail: Optional[str]
    publication_date: Optional[str]
    last_updated_date: Optional[str]
    author: Optional[str]
    full_article_text: str
    video_duration: Optional[str]
    word_count: Optional[str]
    lang: Optional[str]
    description: Optional[str]


# The SitemapParser class is designed to handle the parsing of sitemaps,
# which are XML files used by websites to list their pages for search engines

class SitemapParser:

    #Constructor
    def __init__(self, index_url: str):
        self.index_url = index_url


    #This method returns a list of strings, where each string is a URL to a monthly sitemap
    def get_monthly_sitemap_urls(self) -> List[str]:
        # The method sends an HTTP GET request to the URL stored in self.index_url using the requests.get() function.
        # This URL is expected to point to a sitemap index file, which is an XML document listing other sitemaps (usually organized by month).
        response = requests.get(self.index_url) # it is a url of a website
        # Parsing the XML Content
        soup = BeautifulSoup(response.content, 'xml')
        # The method soup.find_all('loc') searches the parse tree for all <loc> elements.
        # In a sitemap, these elements usually contain URLs to other sitemaps
        # urls is a list comprehension is used to extract the text content of each <loc> element and store it in a list called urls
        urls = [loc.text for loc in soup.find_all('loc')]
        print("Monthly sitemap URLs:", urls)  # Debug output
        return urls

    #get_article_urls is used to extract article URLs from a given monthly sitemap URL

    # input is : the URL of the monthly sitemap, which is expected to be an XML file containing URLs of individual articles.
    # Returns a list of strings, where each string is a URL to an article.

    def get_article_urls(self, monthly_sitemap_url: str) -> List[str]:
        try:
            # Sends HTTP GET request to the monthly_sitemap_url using requests.get(), which fetches the content of the sitemap.
            response = requests.get(monthly_sitemap_url)
            # Parsing the XML Content
            soup = BeautifulSoup(response.content, 'xml')
            # Extract and encode URLs from <loc> tags
            urls = []
            for loc in soup.find_all('loc'):
                url = loc.text
                encoded_url = quote(url, safe=':/')  # Encode the URL, keep ':' and '/' as is
                urls.append(encoded_url)

            print(f"Article URLs from {monthly_sitemap_url}:", urls)  # Debug output
            return urls
        except requests.RequestException as e:
            print(f"Error fetching the sitemap: {e}")
            return []
        except Exception as e:
            print(f"Error parsing the sitemap: {e}")
            return []

#The ArticleScraper class is designed to
#scrape articles from web pages, extracting both metadata (from a JSON script tag) and the full article text.
# and then encapsulate the information into an Article object.

class ArticleScraper:
    # constructor
    def __init__(self):
        #The pass statement means that no specific attributes or actions are taken when an instance of ArticleScraper is created.
        pass

    # input : article_url(str) A string representing the URL of the article to be scraped.
    # Return : Article or non

    def scrape_article(self, article_url: str) -> Article:
        try:
            # 1. Fetching the web page
            response = requests.get(article_url)
            response.raise_for_status()  # Raise an exception for HTTP errors

            # 2. Parsing the web page content
            soup = BeautifulSoup(response.content, 'html.parser')

            # 3. Removing unwanted elements
            unwanted_selectors = [
                '.lg_para.summary',
                '.footer-bottom-text',
                '.footer_top_menu',
                '.footer_middle_menu',
                '.footer_btm_row',
                '.col-4',
                '.post-type.post-metas.type-wrap.article-details-metas',
                '.post_disclaimer'
            ]

            # Remove each unwanted element from the soup
            for selector in unwanted_selectors:
                for element in soup.select(selector):
                    element.decompose()

            # 4. extracting metadata
                #Search the HTML for a <script> tag with the attribute type="text/tawsiyat".
            script_tag = soup.find('script', {'type': 'text/tawsiyat'}) #script_tag is a BeautifulSoup Object

            metadata = {}
                #check if the script tag is found
            if script_tag:
                #Extract the content of the script tag
                #In BeautifulSoup, the .string attribute is used to access the content of a tag
                # if that tag contains only a single string of text
                metadata_contact = script_tag.string #This line assigns the extracted text (the JSON string) from the <script> tag to the variable metadata_content.


                # Parse the contact as Json
                try:
                    #Attempts to parse the text content of the <script> tag as JSON
                    metadata = json.loads(script_tag.string)
                    # check if the type is 'article'
                    is_article = metadata.get('type') == 'article'
                except json.JSONDecodeError:
                    print(f"Failed to parse JSON in script tag for {article_url}")
                    is_article = False
                except Exception as e:
                    print(f"Error parsing script tag: {e}")

            else:
                print("The <script type='text/tawsiyat'> tag was not found")
                is_article = False

            # Only proceed if the page type is 'article'
            # 5. extracting the full article text

            if is_article:
                # Find the specific section by class
                section = soup.find('section',{'class':'read-section'})

                # If the section exists, find the specific div inside it
                if section:
                    div_content = section.find('div', {'class':'p-content'})

                    #If the div exists, extract the text from all <p> tags within it
                    if div_content:
                        # Extract and print the paragraphs to debug the order
                        paragraphs = [p.get_text() for p in div_content.find_all('p')]

                        print("Extracted paragraphs (before any modification):")
                        for idx, para in enumerate(paragraphs):
                            print(f"Paragraph {idx + 1}: {para}")

                        if metadata.get('lang') == 'ar':
                            paragraphs.reverse()  # Reverse the order if the issue is persistent for Arabic

                        full_article_text = ' '.join(paragraphs)


                        # soup.find_all('p'): Finds all <p> (paragraph) tags in the HTML.
                        # p.get_text(): Extracts the text from each paragraph.
                        # .join(...): Joins all the extracted paragraph texts into a single string,
                        # separated by spaces, to form the full text of the article.
                        #full_article_text = ' '.join(p.get_text() for p in soup.find_all('p'))


                        # 5. Creating an Article Object
                        article = Article(
                            url=article_url,
                            post_id=metadata.get('postid'),
                            title=metadata.get('title'),
                            keywords=metadata.get('keywords', []),
                            thumbnail=metadata.get('thumbnail'),
                            publication_date=metadata.get('published_time'),
                            last_updated_date=metadata.get('last_updated'),
                            author=metadata.get('author'),
                            full_article_text=full_article_text,
                            video_duration=metadata.get('video_duration'),
                            word_count=metadata.get('word_count'),
                            lang=metadata.get('lang'),
                            description=metadata.get('description'),
                        )
                        print(f"Scraped article {article_url}: {article}")
                        return article
                    else:
                        print("The <div class = 'p-content'> was not found within the specified section, so there is no article.")
                        return None
                else:
                    print("The <section> with the specified classes was not found, so not article, error in metadata")
                    return None
            else:
                print("The page is not recognized as an article. No text extracted.")
                return None

        except requests.RequestException as e:
            print(f"Failed to fetch {article_url}: {e}")
        except Exception as e:
            print(f"An error occurred while scraping {article_url}: {e}")
        return None



class FileUtility:
    @staticmethod
    def save_articles_to_json(year, month, articles, compressed=False):
        # Handle special cases for filenames
        if year == "all_years" and month == "all_months":
            filename = 'all_articles_originaltemp.json.gz' if compressed else 'all_articles_originaltemp.json'
        else:
            # Convert month to an integer for proper formatting
            try:
                int_month = int(month)
                filename = f'articles_{year}_{int_month:02d}.json.gz' if compressed else f'articles_{year}_{int_month:02d}.json'
            except ValueError:
                print(f"Invalid month value: {month}. Defaulting to 'articles.json'")
                filename = 'articles.json.gz' if compressed else 'articles.json'

        # Create a directory to save the files if it doesn't exist
        if not os.path.exists('data'):
            os.makedirs('data')
        filepath = os.path.join('data', filename)

        # Save the data to the JSON file
        try:
            # Open the file with gzip compression if compressed is True
            open_function = gzip.open if compressed else open

            # Write to the file
            with open_function(filepath, 'wt', encoding='utf-8') as f:
                json.dump([article.__dict__ for article in articles], f, ensure_ascii=False, indent=4)

            print(f'Successfully saved to {filepath}')
        except Exception as e:
            print(f'Error saving file {filepath}: {e}')



def main():
    sitemap_index_url = 'https://www.almayadeen.net/sitemaps/all.xml'
    sitemap_parser = SitemapParser(sitemap_index_url)

    monthly_sitemap_urls = sitemap_parser.get_monthly_sitemap_urls()
    all_articles_original = []

    scraped_count = 0
    max_articles = 5 # Maximum number of articles to scrape

    for monthly_url in monthly_sitemap_urls:
        try:
            year_month = monthly_url.split('-')[-3:-1]
            year, month = year_month[0], year_month[1]
        except IndexError as e:
            print(f"Could not extract year and month from URL: {monthly_url}. Error: {e}")
            continue

        article_urls = sitemap_parser.get_article_urls(monthly_url)
        monthly_articles = []

        for article_url in article_urls:
            try:
                if scraped_count >= max_articles:
                    print(f"Reached the limit of {max_articles} articles. Stopping.")
                    break

                article = ArticleScraper().scrape_article(article_url)
                if article:
                    monthly_articles.append(article)
                    scraped_count += 1
                    print(f"articles scrapped till now: {scraped_count}")

            except Exception as e:
                print(f"Failed to scrape article {article_url}: {e}")

        all_articles_original.extend(monthly_articles)

        # Optionally save articles for the current month if you want to save incrementally
        if monthly_articles:
            FileUtility.save_articles_to_json(year, month, monthly_articles, compressed=True)
            print(f"Saved {len(monthly_articles)} articles for {year}-{month}")

        # Break the outer loop if the limit is reached
        if scraped_count >= max_articles:
            print(f"Reached the limit of {max_articles} articles. Stopping.")
            break

    print(f"Total articles scraped: {scraped_count}")

    # Optionally save all scraped articles
    if all_articles_original:
        FileUtility.save_articles_to_json("all_years", "all_months", all_articles_original, compressed=True)
        print(f"Saved a total of {len(all_articles_original)} articles.")


if __name__ == "__main__":
    main()