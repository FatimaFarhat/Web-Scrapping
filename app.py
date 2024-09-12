from flask import Flask, jsonify, request
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime, timedelta
from flask import Flask, jsonify, request



app = Flask(__name__)  # Initialize a Flask application

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")  # Establish connection with MongoDB server running locally
db = client["almayadeen"]  # Access 'almayadeen' database
collection = db["articles"]  # Access 'articles' collection within 'almayadeen' database

# Error handling function to return a standardized error response
def handle_error(message, status_code=400):
    response = jsonify({"error": message})
    response.status_code = status_code
    return response

# 1. Top Keywords Endpoint: /top_keywords
@app.route('/top_keywords', methods=['GET'])
def top_keywords():
    # Pipeline to unwind keywords array, group by keyword, count occurrences, sort by frequency, and limit to top 10
    pipeline = [
        {"$unwind": "$keywords"},  # Unwind the 'keywords' array
        {"$addFields": {"keywords": {"$split": ["$keywords", ","]}}},  # Split the keywords by comma
        {"$unwind": "$keywords"},  # Unwind the newly split array of individual keywords
        {"$group": {"_id": "$keywords", "count": {"$sum": 1}}},
        # Group by each individual keyword and count occurrences
        {"$sort": {"count": -1}},  # Sort by count in descending order
        {"$limit": 10},  # Limit the result to the top 10 keywords
        {"$project": {"keyword": "$_id", "count": 1}}  # Project keyword as 'keyword' and keep 'count'
    ]
    try:
        result = list(collection.aggregate(pipeline))  # Execute the aggregation pipeline
        # Ensure Unicode text is properly displayed
        for item in result:
            item["_id"] = item["_id"]  # No transformation needed as jsonify should handle it
        return jsonify(result)  # Return the result in JSON format
    except Exception as e:
        return handle_error(f"Error fetching top keywords: {str(e)}")  # Handle potential errors

# 2. Top Authors Endpoint: /top_authors
@app.route('/top_authors', methods=['GET'])
def top_authors():
    # Pipeline to group articles by author, count the number of articles per author, sort and limit results
    pipeline = [
        {"$group": {"_id": "$author", "count": {"$sum": 1}}},  # Groups by author, counting articles
        {"$sort": {"count": -1}},  # Sort by count of articles in descending order
        {"$limit": 10}  # Return top 10 authors
    ]

    try:
        result = list(collection.aggregate(pipeline))  # Execute the aggregation pipeline
        return jsonify(result)  # Return the result in JSON format
    except Exception as e:
        return handle_error(f"Error fetching top authors: {str(e)}")  # Handle potential errors

# 3. Articles by Date Endpoint: /articles_by_date
@app.route('/articles_by_date', methods=['GET'])
def articles_by_date():
    # Pipeline to convert string date field into date object, group by date, and count articles per date
    pipeline = [
        {"$addFields": {
            "publication_date": {
                "$cond": {
                    "if": {"$and": [{"$ne": ["$publication_date", None]}, {"$ne": ["$publication_date", ""]}]},
                    "then": {"$dateFromString": {"dateString": "$publication_date"}},  # Converts string date to date object
                    "else": None
                }
            }
        }},
        {"$match": {"publication_date": {"$ne": None}}},  # Filter out documents with null or invalid dates
        {"$group": {"_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$publication_date"}},
                    "count": {"$sum": 1}}},  # Group by date and count articles
        {"$sort": {"_id": 1}}  # Sort by date in ascending order
    ]

    try:
        result = list(collection.aggregate(pipeline))  # Execute the aggregation pipeline
        return jsonify(result)  # Return the result in JSON format
    except Exception as e:
        return handle_error(f"Error fetching articles by date: {str(e)}")  # Handle potential errors

# 4. Articles by Word Count Endpoint: /articles_by_word_count
@app.route('/articles_by_word_count', methods=['GET'])
def articles_by_word_count():
    # Pipeline to clean, group articles by word count, and count occurrences
    pipeline = [
        {
            "$addFields": {
                # Extract numeric value from word_count string and convert it to an integer
                "word_count_int": {
                    "$toInt": {
                        "$arrayElemAt": [
                            {"$split": [
                                {"$trim": {"input": "$word_count"}},  # Remove spaces
                                " "
                            ]},
                            0  # Extract the first element, which is the number
                        ]
                    }
                }
            }
        },
        {
            "$group": {
                "_id": "$word_count_int",  # Group by the integer word count
                "article_count": {"$sum": 1}  # Count occurrences of each word count
            }
        },
        {
            "$sort": {"_id": -1}  # Sort by word count in descending order
        }
    ]

    try:
        result = list(collection.aggregate(pipeline))  # Execute the aggregation pipeline

        # Format the result to display 'word count' and 'article count'
        formatted_result = [
            {"word_count": f"{doc['_id']} words", "article_count": doc['article_count']}
            for doc in result
        ]

        return jsonify(formatted_result)  # Return the result in a JSON format
    except Exception as e:
        return handle_error(f"Error fetching articles by word count: {str(e)}")  # Handle errors

# 5. Articles by Language Endpoint: /articles_by_language
@app.route('/articles_by_language', methods=['GET'])
def articles_by_language():
    # Pipeline to group articles by their language and count occurrences
    pipeline = [
        {"$group": {"_id": "$lang", "count": {"$sum": 1}}},  # Groups by language, counting articles
        {"$sort": {"count": -1}}  # Sort by count in descending order
    ]

    try:
        result = list(collection.aggregate(pipeline))  # Execute the aggregation pipeline
        return jsonify(result)  # Return the result in JSON format
    except Exception as e:
        return handle_error(f"Error fetching articles by language: {str(e)}")  # Handle potential errors

#6. Articles by Category
@app.route('/articles_by_classes', methods=['GET'])
def articles_by_classes():
    # Pipeline to extract and count categories from the 'classes' array field
    pipeline = [
        {
            "$unwind": "$classes"  # Unwind the 'classes' array to get each class element
        },
        {
            "$match": {
                "classes.mapping": "category"  # Only include documents where 'mapping' is 'category'
            }
        },
        {
            "$group": {
                "_id": "$classes.value",  # Group by the 'value' field of 'classes'
                "count": {"$sum": 1}  # Count the number of articles in each category
            }
        },
        {
            "$sort": {"count": -1}  # Sort by count in descending order
        }
    ]

    try:
        result = list(collection.aggregate(pipeline))  # Execute the aggregation pipeline
        return jsonify(result)  # Return the result in JSON format
    except Exception as e:
        return handle_error(f"Error fetching articles by category: {str(e)}")  # Handle potential errors


# 7. Recent Articles Endpoint: /recent_articles
@app.route('/recent_articles', methods=['GET'])
def recent_articles():
    # Pipeline to sort by the publication date and limit to the 10 most recent articles
    pipeline = [
        {
            # Add field to convert 'publication_date' to an ISODate format
            "$addFields": {
                "parsed_publication_date": {
                    "$dateFromString": {
                        "dateString": "$publication_date",
                        "onError": None,  # Handle any parsing errors by setting the date to None
                        "onNull": None  # Handle missing dates by setting the date to None
                    }
                }
            }
        },
        {
            # Filter out documents where the publication date could not be parsed
            "$match": {"parsed_publication_date": {"$ne": None}}
        },
        {
            # Sort articles by 'parsed_publication_date' in descending order (most recent first)
            "$sort": {"parsed_publication_date": -1}
        },
        {
            # Limit to the 10 most recent articles
            "$limit": 10
        }
    ]

    try:
        # Execute the aggregation pipeline
        result = list(collection.aggregate(pipeline))

        # Convert ObjectId to string for JSON serialization
        for article in result:
            if '_id' in article:
                article['_id'] = str(article['_id'])  # Convert ObjectId to string

        return jsonify(result)  # Return the result in JSON format
    except Exception as e:
        return handle_error(f"Error fetching recent articles: {str(e)}")  # Handle potential errors


#8. Articles by Keyword

@app.route('/articles_by_keyword/<keyword>', methods=['GET'])
def articles_by_keyword(keyword):
    """
    Endpoint to retrieve a list of articles that contain a specific keyword.
    Returns a JSON array of articles with their titles.
    """
    # Define the query to search for articles containing the specific keyword
    query = {
        "keywords": {
            "$regex": keyword,  # Use regex to search for the keyword in the keywords field
            "$options": "i"  # Case-insensitive search
        }
    }

    try:
        # Fetch the articles that match the keyword query
        articles = list(collection.find(query, {"title": 1, "_id": 0}))

        # Count the number of matching articles
        article_count = len(articles)

        if article_count == 0:
            return jsonify({"message": f"No articles found for keyword: {keyword}"}), 404

        return jsonify({
            "count": article_count,  # Include the count of articles
            "articles": articles  # Include the list of articles
        })
    except Exception as e:
        return handle_error(f"Error fetching articles by keyword: {str(e)}")  # Handle potential errors
#9. Articles by Author

@app.route('/articles_by_author/<author_name>', methods=['GET'])
def articles_by_author(author_name):
    """
    Endpoint to retrieve all articles written by a specific author.
    Returns a JSON array of articles with their titles and the total count of matching articles.
    """
    # Define the query to search for articles by the author
    query = {
        "author": {
            "$regex": author_name,  # Use regex to search for the author name in the author field
            "$options": "i"  # Case-insensitive search
        }
    }

    try:
        # Fetch the articles that match the author name query
        articles = list(collection.find(query, {"title": 1, "_id": 0}))

        # Count the number of matching articles
        article_count = len(articles)

        if article_count == 0:
            return jsonify({"message": f"No articles found for author: {author_name}"}), 404

        return jsonify({
            "count": article_count,  # Include the count of articles
            "articles": articles  # Include the list of articles
        })
    except Exception as e:
        return handle_error(f"Error fetching articles by author: {str(e)}")  # Handle potential errors

#10. Top Classes
@app.route('/top_classes', methods=['GET'])
def top_classes():
    # Define the aggregation pipeline to extract and count class values
    pipeline = [
        {
            "$unwind": "$classes"  # Deconstruct the 'classes' array into individual documents
        },
        {
            "$group": {
                "_id": "$classes.value",  # Group by the class value
                "count": {"$sum": 1}  # Count the number of occurrences of each class
            }
        },
        {
            "$sort": {"count": -1}  # Sort by count in descending order
        },
        {
            "$limit": 10  # Limit the result to the top 10 classes
        }
    ]

    try:
        result = list(collection.aggregate(pipeline))  # Execute the aggregation pipeline
        # Format the result for better readability
        formatted_result = [{"class": item["_id"], "count": item["count"]} for item in result]
        return jsonify(formatted_result)  # Return the result in JSON format
    except Exception as e:
        return handle_error(f"Error fetching top classes: {str(e)}")  # Handle potential errors

#11. Article Details

@app.route('/article_details/<postid>', methods=['GET'])
def article_details(postid):
    """
    Endpoint to retrieve detailed information of a specific article based on its postid.
    Returns detailed information including URL, title, keywords, and other metadata.
    """
    # Define the query to search for the article by postid
    query = {"post_id": postid}

    try:
        # Fetch the article that matches the postid
        article = collection.find_one(query, {
            "url": 1,
            "title": 1,
            "keywords": 1,
            "author": 1,
            "publication_date": 1,
            "last_updated_date": 1,
            "full_article_text": 1,
            "thumbnail": 1,
            "video_duration": 1,
            "_id": 0  # Exclude MongoDB ObjectId from the result
        })

        # If no article is found, return a 404 response
        if not article:
            return jsonify({"message": f"No article found for postid: {postid}"}), 404

        return jsonify(article)
    except Exception as e:
        return handle_error(f"Error fetching article details: {str(e)}")  # Handle potential errors



#12. Articles Containing Videos

@app.route('/articles_with_video', methods=['GET'])
def articles_with_video():
    """
    Endpoint to retrieve a list of articles that contain a video.
    Articles are filtered to include only those where 'video_duration' is not null.
    Returns a JSON array of articles with their titles, video durations, and ObjectIds.
    """
    # Define the aggregation pipeline
    pipeline = [
        {
            "$match": {
                "video_duration": {"$ne": None}  # Filter for documents where video_duration is not null
            }
        },
        {
            "$addFields": {
                "_id": {"$toString": "$_id"}  # Convert the ObjectId to a string
            }
        },
        {
            "$project": {
                "_id": 1,  # Include the MongoDB ObjectId field (as a string) in the result
                "title": 1,  # Include the title field in the result
                "video_duration": 1,  # Include the video_duration field in the result
            }
        }
    ]

    try:
        result = list(collection.aggregate(pipeline))  # Execute the aggregation pipeline
        return jsonify(result)  # Return the result in JSON format
    except Exception as e:
        return handle_error(f"Error fetching articles with video: {str(e)}")  # Handle potential errors

# 13. Articles by Publication Year

@app.route('/articles_by_year/<int:year>', methods=['GET'])
def articles_by_year(year):
    """
    Endpoint to retrieve the number of articles published in a specific year.
    Returns the count of articles for the given year.
    """
    # Define the start and end dates for the year
    start_date = f"{year}-01-01T00:00:00Z"
    end_date = f"{year}-12-31T23:59:59Z"

    # Define the query to search for articles within the specified year
    query = {
        "publication_date": {
            "$gte": start_date,
            "$lte": end_date
        }
    }

    try:
        # Count the number of articles published in the given year
        article_count = collection.count_documents(query)

        # If no articles are found, return a 404 response
        if article_count == 0:
            return jsonify({"message": f"No articles found for the year {year}"}), 404

        # Return the count of articles for the year
        return jsonify({
            "year": year,
            "article_count": article_count
        })
    except Exception as e:
        return handle_error(f"Error fetching articles by year: {str(e)}")  # Handle potential errors

#14. Longest Articles
@app.route('/longest_articles', methods=['GET'])
def longest_articles():
    """
    Endpoint to retrieve the top 10 articles with the highest word count.
    Returns a JSON array of articles with their titles and word counts.
    """
    # Define the aggregation pipeline
    pipeline = [
        {
            "$addFields": {
                "word_count_int": {"$toInt": "$word_count"}  # Convert word_count to integer for proper sorting
            }
        },
        {
            "$sort": {"word_count_int": -1}  # Sort by word count in descending order
        },
        {
            "$limit": 10  # Limit to the top 10 longest articles
        },
        {
            "$project": {
                "title": 1,  # Include only the title in the result
                "word_count_int": 1,  # Include the word count in the result
                "_id": 0  # Exclude the MongoDB ObjectId from the result
            }
        }
    ]

    try:
        result = list(collection.aggregate(pipeline))  # Execute the aggregation pipeline
        # Format the result to include word count in the response
        formatted_result = [{"title": doc["title"], "word_count": f"{doc['word_count_int']} words"} for doc in result]
        return jsonify(formatted_result)  # Return the result in JSON format
    except Exception as e:
        return handle_error(f"Error fetching longest articles: {str(e)}")  # Handle potential errors

#15. Shortest Articles
@app.route('/shortest_articles', methods=['GET'])
def shortest_articles():
    """
    Endpoint to retrieve the top 10 articles with the lowest word count.
    Returns a JSON array of articles with their titles and word counts.
    """
    # Define the aggregation pipeline
    pipeline = [
        {
            "$addFields": {
                "word_count_int": {"$toInt": "$word_count"}  # Convert word_count to integer for proper sorting
            }
        },
        {
            "$sort": {"word_count_int": 1}  # Sort by word count in ascending order
        },
        {
            "$limit": 10  # Limit to the top 10 shortest articles
        },
        {
            "$project": {
                "title": 1,  # Include only the title in the result
                "word_count_int": 1,  # Include the word count in the result
                "_id": 0  # Exclude the MongoDB ObjectId from the result
            }
        }
    ]

    try:
        result = list(collection.aggregate(pipeline))  # Execute the aggregation pipeline
        # Format the result to include word count in the response
        formatted_result = [{"title": doc["title"], "word_count": f"{doc['word_count_int']} words"} for doc in result]
        return jsonify(formatted_result)  # Return the result in JSON format
    except Exception as e:
        return handle_error(f"Error fetching shortest articles: {str(e)}")  # Handle potential errors


#16. Articles by keywords count
@app.route('/articles_by_keyword_count', methods=['GET'])
def articles_by_keyword_count():
    """
    Endpoint to retrieve the number of articles grouped by the number of keywords they contain.
    Returns a JSON array of counts where each entry includes the number of keywords and the count of articles with that many keywords.
    """
    # Define the aggregation pipeline
    pipeline = [
        {
            "$addFields": {
                "keywords_array": {
                    "$cond": {
                        "if": {"$isArray": "$keywords"},  # Check if 'keywords' is already an array
                        "then": "$keywords",  # If true, use 'keywords' as is
                        "else": {"$split": [{"$ifNull": ["$keywords", ""]}, ","]}  # Convert to array if it is a string
                    }
                }
            }
        },
        {
            "$addFields": {
                "keyword_count": {"$size": "$keywords_array"}  # Count the number of keywords in each article
            }
        },
        {
            "$group": {
                "_id": "$keyword_count",  # Group by the keyword count
                "article_count": {"$sum": 1}  # Count the number of articles for each keyword count
            }
        },
        {
            "$sort": {"_id": 1}  # Sort by keyword count in ascending order
        }
    ]

    try:
        result = list(collection.aggregate(pipeline))  # Execute the aggregation pipeline
        # Format the result for better readability
        formatted_result = [{"keyword_count": entry["_id"], "article_count": entry["article_count"]} for entry in result]
        return jsonify(formatted_result)  # Return the result in JSON format
    except Exception as e:
        return handle_error(f"Error fetching articles by keyword count: {str(e)}")  # Handle potential errors

# 17. Articles with thumbnail
@app.route('/articles_with_thumbnail', methods=['GET'])
def articles_with_thumbnail():
    """
    Endpoint to retrieve a list of articles that have a thumbnail image.
    Articles are filtered to include only those where 'thumbnail' is not null.
    Returns a JSON array of article titles with their thumbnails.
    """
    # Define the aggregation pipeline
    pipeline = [
        {
            "$match": {
                "thumbnail": {"$ne": None}  # Filter for documents where thumbnail is not null
            }
        },
        {
            "$project": {
                "title": 1,   # Include only the title field in the result
                "_id": 0      # Exclude the MongoDB ObjectId from the result
            }
        }
    ]

    try:
        # Execute the aggregation pipeline
        result = list(collection.aggregate(pipeline))
        # Format the result for better readability
        formatted_result = [entry["title"] for entry in result]
        return jsonify(formatted_result)  # Return the result in JSON format
    except Exception as e:
        return handle_error(f"Error fetching articles with thumbnail: {str(e)}")  # Handle potential errors


#18. Articles Updated After Publication
@app.route('/articles_updated_after_publication', methods=['GET'])
def articles_updated_after_publication():
    """
    Endpoint to retrieve a list of articles where the last_updated_date is after the publication_date.
    Returns a JSON array of articles with their titles.
    """
    # Define the aggregation pipeline
    pipeline = [
        {
            "$addFields": {
                "publication_date": {
                    "$dateFromString": {"dateString": "$publication_date"}  # Convert publication_date to a date object
                },
                "last_updated_date": {
                    "$dateFromString": {"dateString": "$last_updated_date"}  # Convert last_updated_date to a date object
                }
            }
        },
        {
            "$match": {
                "$expr": {
                    "$gt": ["$last_updated_date", "$publication_date"]  # Match documents where last_updated_date > publication_date
                }
            }
        },
        {
            "$project": {
                "title": 1,  # Include only the title in the result
                "_id": 0     # Exclude the MongoDB ObjectId from the result
            }
        }
    ]

    try:
        # Execute the aggregation pipeline
        result = list(collection.aggregate(pipeline))
        # Return the result in JSON format
        return jsonify(result)
    except Exception as e:
        # Handle potential errors
        return handle_error(f"Error fetching articles updated after publication: {str(e)}")

#19. Articles by Coverage
@app.route('/articles_by_coverage/<coverage>', methods=['GET'])
def articles_by_coverage(coverage):
    """
    Endpoint to retrieve a list of articles under a specific coverage category.
    Articles are filtered to include only those where the coverage matches the specified value.
    Returns a JSON array of articles with their titles.
    """
    # Define the aggregation pipeline
    pipeline = [
        {
            "$unwind": "$classes"  # Deconstruct the 'classes' array field
        },
        {
            "$match": {
                "classes.mapping": "coverage",  # Match documents where the 'mapping' is 'coverage'
                "classes.value": coverage  # Match documents where the 'value' is the specified coverage
            }
        },
        {
            "$project": {
                "title": 1,  # Include only the title field in the result
                "_id": 0     # Exclude the MongoDB ObjectId from the result
            }
        }
    ]

    try:
        # Execute the aggregation pipeline
        result = list(collection.aggregate(pipeline))
        # Return the result in JSON format
        return jsonify(result)
    except Exception as e:
        # Handle potential errors
        return handle_error(f"Error fetching articles by coverage: {str(e)}")

#20. Most Popular Keywords in the Last X Days
@app.route('/popular_keywords_last_X_days/<int:days>', methods=['GET'])
def popular_keywords_last_X_days(days):
    """
    Endpoint to get the most popular keywords in the last X days.
    """
    try:
        # Calculate the date X days ago from today
        start_date = datetime.utcnow() - timedelta(days=days)

        # Convert start_date to ISO 8601 string for MongoDB query
        start_date_str = start_date.isoformat()

        # Define the aggregation pipeline
        pipeline = [
            # Match articles published in the last X days
            {
                "$match": {
                    "publication_date": {"$gte": start_date_str}
                }
            },
            # Split the comma-separated keywords into an array
            {
                "$addFields": {
                    "keywords_array": {"$split": ["$keywords", ","]}
                }
            },
            # Unwind the keywords array to process each keyword individually
            {
                "$unwind": "$keywords_array"
            },
            # Group by each keyword and count occurrences
            {
                "$group": {
                    "_id": "$keywords_array",
                    "count": {"$sum": 1}
                }
            },
            # Sort by count in descending order
            {
                "$sort": {"count": -1}
            },
            # Limit to the top 10 most frequent keywords
            {
                "$limit": 10
            }
        ]

        # Execute the aggregation pipeline
        result = list(collection.aggregate(pipeline))

        # Return the result in JSON format
        return jsonify(result)

    except Exception as e:
        # Handle potential errors
        return handle_error(f"Error fetching popular keywords: {str(e)}")

#21. Articles by Published Month
@app.route('/articles_by_month/<int:year>/<int:month>', methods=['GET'])
def articles_by_month(year, month):
    """
    Endpoint to retrieve the number of articles published in a specific month and year.
    Articles are grouped by month and year.
    Returns a JSON object with the count of articles.
    """
    # Define the start and end dates for the given month
    start_date = datetime(year, month, 1)
    end_date = datetime(year, month + 1, 1) if month < 12 else datetime(year + 1, 1, 1)

    # Define the aggregation pipeline
    pipeline = [
        {
            "$match": {
                "publication_date": {
                    "$gte": start_date.isoformat(),
                    "$lt": end_date.isoformat()
                }
            }
        },
        {
            "$group": {
                "_id": None,
                "count": {"$sum": 1}
            }
        }
    ]

    try:
        # Execute the aggregation pipeline
        result = list(collection.aggregate(pipeline))
        count = result[0]['count'] if result else 0
        return jsonify({f"{start_date.strftime('%B %Y')}": count})
    except Exception as e:
        return jsonify({"error": f"Error fetching articles by month: {str(e)}"})

#22. Articles by Word Count Range
@app.route('/articles_by_word_count_range/<int:min_word_count>/<int:max_word_count>', methods=['GET'])
def articles_by_word_count_range(min_word_count, max_word_count):
    """
    Endpoint to retrieve articles with a word count within a specified range.
    Returns a JSON object with the count of articles for the given word count range.
    """
    # Define the aggregation pipeline
    pipeline = [
        {
            "$addFields": {
                "word_count_int": {"$toInt": "$word_count"}  # Ensure word_count is an integer
            }
        },
        {
            "$match": {
                "word_count_int": {
                    "$gte": min_word_count,
                    "$lte": max_word_count
                }
            }
        },
        {
            "$group": {
                "_id": None,
                "count": {"$sum": 1}
            }
        }
    ]

    try:
        # Execute the aggregation pipeline
        result = list(collection.aggregate(pipeline))
        count = result[0]['count'] if result else 0
        return jsonify({
            f"Articles between {min_word_count} and {max_word_count} words": count
        })
    except Exception as e:
        return jsonify({"error": f"Error fetching articles by word count range: {str(e)}"})

#23. Articles with Specific Keyword Count

@app.route('/articles_with_specific_keyword_count/<int:count>', methods=['GET'])
def articles_with_specific_keyword_count(count):
    """
    Endpoint to retrieve articles that contain exactly a specified number of keywords.
    Returns a JSON object with the count of articles for the given keyword count.
    """
    pipeline = [
        {
            "$match": {
                "keywords": {"$ne": None}  # Ensure the 'keywords' field is not null or missing
            }
        },
        {
            "$addFields": {
                "keywords_array": {
                    "$filter": {
                        "input": {"$split": ["$keywords", ","]},  # Split the keywords string into an array
                        "as": "keyword",
                        "cond": {"$ne": [{"$trim": {"input": "$$keyword"}}, ""]}
                        # Remove empty keywords and trim spaces
                    }
                }
            }
        },
        {
            "$addFields": {
                "keyword_count": {"$size": "$keywords_array"}  # Count the number of keywords in the array
            }
        },
        {
            "$match": {
                "keyword_count": count  # Match documents where the keyword count is exactly as specified
            }
        },
        {
            "$group": {
                "_id": None,
                "count": {"$sum": 1}  # Count the number of matching articles
            }
        }
    ]

    try:
        # Execute the aggregation pipeline
        result = list(collection.aggregate(pipeline))
        count_result = result[0]['count'] if result else 0
        return jsonify({
            f"Articles with exactly {count} keywords": count_result
        })
    except Exception as e:
        return jsonify({"error": f"Error fetching articles with specific keyword count: {str(e)}"})

#24.  Articles by Specific Date

@app.route('/articles_by_specific_date/<date>', methods=['GET'])
def articles_by_specific_date(date):
    """
    Endpoint to retrieve articles published on a specific date.
    The date should be provided in the format 'YYYY-MM-DD'.
    """
    try:
        # Check if the input date is in correct format
        target_date = datetime.strptime(date, '%Y-%m-%d')

        # MongoDB query to match the date part of publication_date (ignoring the time)
        # Check if the input date is in correct format
        target_date = datetime.strptime(date, '%Y-%m-%d')

        # MongoDB query to match the date part of publication_date (ignoring the time)
        query = {
            "publication_date": {
                "$regex": f"^{date}"  # Match the date as a string (e.g., "2024-09-04")
            }
        }

        # Fetch articles from MongoDB
        articles = list(collection.find(query, {"title": 1, "publication_date": 1, "_id": 0}))

        # Get the count of articles
        article_count = len(articles)

        # If no articles found
        if not articles:
            return jsonify({"message": f"No articles found for {date}"}), 404

        # Return the number of articles and the list of articles
        return jsonify({
            "date": date,
            "article_count": article_count,
            "articles": articles
        })

    except ValueError:
        # Handle invalid date format
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400
    except Exception as e:
        # Handle other errors
        return jsonify({"error": f"Error fetching articles by specific date: {str(e)}"}), 500

# 25. Articles Containing Specific Text

@app.route('/articles_containing_text/<text>', methods=['GET'])
def articles_containing_text(text):
    """
    Endpoint to retrieve articles that contain a specific text in their content.
    The text will be searched within the 'full_article_text' field.
    """
    try:
        # MongoDB query to search for the text in full_article_text field using regex
        query = {
            "full_article_text": {
                "$regex": text,  # Case-sensitive search for the text
                "$options": "i"  # 'i' option for case-insensitive matching
            }
        }

        # Fetch articles from MongoDB
        articles = list(collection.find(query, {"title": 1, "full_article_text": 1, "_id": 0}))

        # Get the count of articles
        article_count = len(articles)

        # If no articles found
        if not articles:
            return jsonify({"message": f"No articles found containing the text: {text}"}), 404

        # Return the number of articles and the list of articles
        return jsonify({
            "text": text,
            "article_count": article_count,
            #"articles": articles
        })

    except Exception as e:
        # Handle errors
        return jsonify({"error": f"Error fetching articles containing text: {str(e)}"}), 500

#26. Articles with More than N Words
@app.route('/articles_with_more_than/<int:word_count>', methods=['GET'])
def articles_with_more_than(word_count):
    """
    Endpoint to retrieve articles with more than a specified number of words.
    """
    try:
        # MongoDB query to match articles with a word count greater than the specified value
        pipeline = [
            {
                "$match": {
                    "word_count": {
                        "$exists": True,  # Ensure the word_count field exists
                        "$ne": None  # Ensure the word_count is not null
                    }
                }
            },
            {
                "$addFields": {
                    "word_count_int": {
                        "$cond": {
                            "if": {"$isNumber": "$word_count"},
                            "then": "$word_count",
                            "else": {"$toInt": "$word_count"}
                        }
                    }
                }
            },
            {
                "$match": {
                    "word_count_int": {"$gt": word_count}
                    # Filter articles where the converted word_count is greater than the specified value
                }
            },
            {
                "$project": {
                    "title": 1,
                    "word_count_int": 1,
                    "_id": 0
                }
            }
        ]

        articles = list(collection.aggregate(pipeline))

        # If no articles are found
        if not articles:
            return jsonify({"message": f"No articles found with more than {word_count} words"}), 404

        # Return the result with the number of articles found
        return jsonify({
            "word_count": word_count,
            "article_count": len(articles),
            "articles": articles
        })

    except Exception as e:
        # Handle any potential errors
        return jsonify({"error": f"Error fetching articles with more than {word_count} words: {str(e)}"}), 500

# 27. Articles Grouped by Coverage

@app.route('/articles_grouped_by_coverage', methods=['GET'])
def articles_grouped_by_coverage():
    """
    Endpoint to retrieve the number of articles grouped by their coverage category.
    The 'coverage' category is derived from the 'classes' field of each article.
    Returns a JSON object with each coverage category and the count of articles in that category.
    """
    try:
        # Aggregation pipeline to group articles by coverage and count them
        pipeline = [
            {"$unwind": "$classes"},  # Deconstructs the classes array
            {"$match": {"classes.mapping": "coverage"}},  # Filter for coverage mapping
            {"$group": {"_id": "$classes.value", "count": {"$sum": 1}}},  # Group by coverage value and count
            {"$sort": {"count": -1}}  # Sort by count in descending order
        ]

        # Execute the aggregation pipeline
        result = list(collection.aggregate(pipeline))

        # Format the result for the response
        response = [{"coverage": item["_id"], "count": item["count"]} for item in result]

        return jsonify(response)

    except Exception as e:
        return handle_error(f"Error fetching articles grouped by coverage: {str(e)}")

# 28. Articles Published in Last X Hours

@app.route('/articles_last_X_hours/<int:hours>', methods=['GET'])
def articles_last_X_hours(hours):
    """
    Endpoint to retrieve a list of articles published in the last X hours.
    """
    # Calculate the timestamp for X hours ago from now
    start_time = datetime.utcnow() - timedelta(hours=hours)

    # Convert the timestamp to ISO 8601 string format
    start_time_str = start_time.isoformat() + 'Z'

    # Define the query to filter articles published after the start_time
    query = {
        "publication_date": {"$gte": start_time_str}
    }

    try:
        # Find articles that match the query
        articles = list(collection.find(query, {"title": 1, "publication_date": 1, "_id": 0}))

        # Check if any articles were found
        if not articles:
            return jsonify({"message": f"No articles found published in the last {hours} hours"}), 404

        # Return the result in JSON format
        return jsonify(articles)
    except Exception as e:
        # Handle potential errors
        return handle_error(f"Error fetching articles published in the last {hours} hours: {str(e)}")

# 29. Articles by Length of Title
@app.route('/articles_by_title_length', methods=['GET'])
def articles_by_title_length():
    """
    Endpoint to retrieve the number of articles grouped by the length of their title.
    Returns a JSON object with the length of title and count of articles having that length.
    """
    pipeline = [
        {
            "$project": {
                "title_length": { "$strLenCP": "$title" }  # Calculate the length of the title in characters
            }
        },
        {
            "$group": {
                "_id": "$title_length",  # Group by the length of the title
                "count": { "$sum": 1 }   # Count the number of articles for each title length
            }
        },
        {
            "$sort": { "_id": 1 }  # Sort by title length in ascending order
        }
    ]

    try:
        result = list(collection.aggregate(pipeline))  # Execute the aggregation pipeline
        # Format the result
        formatted_result = [{"title_length": item["_id"], "count": item["count"]} for item in result]
        return jsonify(formatted_result)  # Return the result in JSON format
    except Exception as e:
        return handle_error(f"Error fetching articles by title length: {str(e)}")  # Handle potential errors

# 30. Most Updated Articles (Need update)
@app.route('/most_updated_articles', methods=['GET'])
def most_updated_articles():
    """
    Endpoint to retrieve the top 10 articles that have been updated the most times.
    Returns a JSON array of articles with their titles and update counts.
    """
    pipeline = [
        {
            "$sort": { "update_count": -1 }  # Sort by update_count in descending order
        },
        {
            "$limit": 10  # Limit the results to the top 10
        },
        {
            "$project": {
                "title": 1,  # Include the title field
                "update_count": 1,  # Include the update_count field
                "_id": 0  # Exclude the MongoDB ObjectId from the result
            }
        }
    ]

    try:
        result = list(collection.aggregate(pipeline))  # Execute the aggregation pipeline
        return jsonify(result)  # Return the result in JSON format
    except Exception as e:
        return handle_error(f"Error fetching most updated articles: {str(e)}")  # Handle potential errors


# General error handler for invalid routes or methods
@app.errorhandler(404)
def not_found_error(error):
    return handle_error("Endpoint not found", 404)

# General error handler for invalid routes or methods
@app.errorhandler(404)
def not_found_error(error):
    return handle_error("Endpoint not found", 404)




# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)  # Start Flask in debug mode for live error reporting

