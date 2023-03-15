from parsel import Selector
from fastapi.responses import Response
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import requests
import psycopg2
import json
import uvicorn
import openai
import time
import datetime
import schedule

# Set the OpenAI API key
openai.api_key = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"


# Define the function to generate the response
def generate_response(prompt):
    model_engine = "text-davinci-003"
    prompt = (f"{prompt}")
    completions = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5, )
    message = completions.choices[0].text
    return message.strip()


# Connect to the PostgresSQL database
conn = psycopg2.connect(
    host="localhost",
    database="db_hackernews",
    user="postgres",
    password="19012001"
)


# Define the Article model
class Article(BaseModel):
    rank: str
    title: str
    link: str
    shortlink: str
    points: str
    comments: str
    time: str
    author: str
    image_link: str
    content: List[str]
    hashtag: List[str]


app = FastAPI() # Initialize the FastAPI app


@app.get("/")
async def root():
    return {"message": "Welcome to the Hacker News API"}


@app.get("/runs")
async def scrape_and_import():
    # Define the functions
    await scrape_news()
    await import_data()
    return "Scraping and importing completed"

    # Schedule the functions to run every 60 minutes
    schedule.every(60).minutes.do(scrape_and_import)

    # Run the scheduled tasks indefinitely
    while True:
        schedule.run_pending()
        time.sleep(1)


@app.get("/scrape")
async def scrape_news():
    # Initialize the list of news data
    news_data = []

    # Loop over the first 3 pages
    for i in range(3):
        # Construct the URL for the current page
        if i == 0:
            url = "https://news.ycombinator.com/newest"
        else:
            url = f"https://news.ycombinator.com/newest?next={next_id}&n={n}"

        # download the HTML content of the current page

        # Make a GET request to fetch the raw HTML content
        response = requests.get(url)

        # Parse the content of the request with parsel
        selector = Selector(text=response.text)

        # Extract data from the HTML using CSS selectors
        ranks = selector.css(".title .rank::text").getall()
        titles = selector.css(".title a::text").getall()
        links = selector.css(".title a::attr(href)").getall()
        links = [link for link in links if link.startswith("http")]
        short_links = selector.css(".sitestr::text").getall()
        points = selector.css(".score::text").re("\d+")
        comments = selector.css("td.subtext a:last-child::text").re("\d+")
        times = selector.css("span.age::attr(title)").getall()
        authors = selector.css(".hnuser::text").getall()

        # Combine the extracted data into a list of dictionaries
        for rank, title, link, short_link, point, comment, time_post, author, in zip(
                ranks, titles, links, short_links,
                points, comments, times, authors):

            # get the summary of the article using OpenAI
            # prompt = "Summarize (limit about 200 words) the following article: " + title + " " + link
            # response = generate_response(prompt)

            # Make a GET request to fetch the raw HTML content
            try:
                link_request = requests.get(link)
            except requests.exceptions.ConnectionError:
                image_links = None
                contents = None
                hashtags = None
            else:
                if link_request.status_code == 200:
                    link_selector = Selector(text=link_request.text)
                    # get the link of the image, if it exists
                    image_links = link_selector.css("img[src*='jpg']::attr(src)").get()
                    # get the content of the article
                    contents = link_selector.css("p::text").getall()
                    # use the summary from OpenAI
                    # contents = response
                    # get the hashtags of the article
                    hashtags = link_selector.css("a[href*='hashtag']::text").getall()
                elif link_request.status_code == 404:
                    image_links = None
                    contents = None
                    hashtags = None
                else:
                    image_links = None
                    contents = None
                    hashtags = None

            data = {"rank": rank, "title": title, "link": link, "shortlink": short_link, "points": point,
                    "comments": comment, "time": time_post, "author": author, "image_link": image_links,
                    "content": contents, "hashtag": hashtags}
            news_data.append(data)

        # Extract the next_id and n parameters for the next page (if available)
        next_link = selector.css("a.morelink::attr(href)").get()
        if next_link:
            next_id = next_link.split("=")[1].split("&")[0]
            n = next_link.split("=")[2]
    # format the data as JSON look at the JSON structure
    news_json = json.dumps(news_data, indent=4)

    # Write the JSON data to a file every a file
    today = datetime.date.today()
    with open(f"news_data_{today}.json", "w") as f:
        f.write(news_json)

    # Return the JSON-formatted string as a response
    return Response(news_json, media_type="application/json")


# import json to model
@app.get("/import")
async def import_data():
    # Read the JSON data from the file
    today = datetime.date.today()
    with open(f"news_data_{today}.json", "r") as f:
        data = json.load(f)

    # Insert the data into the database
    cur = conn.cursor()
    # delete the old data
    cur.execute("DELETE FROM article")
    # reset the auto increment
    cur.execute("ALTER SEQUENCE article_id_seq RESTART WITH 1")

    for news in data:
        cur.execute("""
            INSERT INTO article (
                rank, title, link, shortlink, points, comments, time, author,
                image_link, content, hashtag
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """, (
            news['rank'],
            news['title'],
            news['link'],
            news['shortlink'],
            news['points'],
            news['comments'],
            news['time'],
            news['author'],
            news['image_link'],
            news['content'],
            news['hashtag'],
        ))
    conn.commit()
    print("Import data successfully!")
    # Close the database connection
    cur.close()
    return {"message": f"Import data successfully!"}


# Create api to get all articles
@app.get("/articles")
def get_articles():
    # Retrieve all articles from the database
    cur = conn.cursor()
    cur.execute("SELECT * FROM article")
    rows = cur.fetchall()
    cur.close()

    # Convert each row to a dictionary and return a list of dictionaries
    result = [
        dict(zip(('id', 'rank', 'title', 'link', 'shortlink', 'points', 'comments', 'time', 'author', 'image_link',
                  'content', 'hashtag'), row)) for row in rows]

    result_json = json.dumps(result, indent=4)
    # Return the article as a dictionary
    return Response(result_json, media_type="application/json")


# Create a new article
@app.post("/articles")
def create_article(article: Article):
    # Insert the new article into the database
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO article (
            rank, title, link, shortlink, points, comments, time, author,
            image_link, content, hashtag
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        ) RETURNING id
    """, (
        article.rank,
        article.title,
        article.link,
        article.shortlink,
        article.points,
        article.comments,
        article.time,
        article.author,
        article.image_link,
        article.content,
        article.hashtag,
    ))
    article_id = cur.fetchone()[0]
    conn.commit()
    cur.close()

    # Return the newly created article with its ID
    return {"id": article_id, **article.dict()}


# Retrieve all articles from the database
@app.get("/articles/{article_id}")
def read_article(article_id: int):
    # Retrieve the article with the given ID from the database
    cur = conn.cursor()
    cur.execute("SELECT * FROM article WHERE id = %s", (article_id,))
    row = cur.fetchone()
    cur.close()

    if row is None:
        # Article with the given ID not found
        raise HTTPException(status_code=404, detail="Article not found")

    result = dict(zip(('id', 'rank', 'title', 'link', 'shortlink', 'points', 'comments', 'time', 'author', 'image_link',
                       'content', 'hashtag'), row))

    result_json = json.dumps(result, indent=4)
    # Return the article as a dictionary
    return Response(result_json, media_type="application/json")


# Update the article with the given ID in the database
@app.put("/articles/{article_id}")
def update_article(article_id: int, article: Article):
    # Update the article with the given ID in the database
    cur = conn.cursor()
    cur.execute("""
        UPDATE article SET
            rank = %s,
            title = %s,
            link = %s,
            shortlink = %s,
            points = %s,
            comments = %s,
            time = %s,
            author = %s,
            image_link = %s,
            content = %s,
            hashtag = %s
        WHERE id = %s
    """, (
        article.rank,
        article.title,
        article.link,
        article.shortlink,
        article.points,
        article.comments,
        article.time,
        article.author,
        article.image_link,
        article.content,
        article.hashtag,
        article_id,
    ))
    if cur.rowcount == 0:
        # Article with the given ID not found
        raise HTTPException(status_code=404, detail="Article not found")
    conn.commit()
    cur.close()
    return {"id": article_id, **article.dict()}


# Delete the article with the given ID from the database
@app.delete("/articles/{article_id}")
async def delete_article(article_id: int):
    # Delete the article with the given ID from the database
    cur = conn.cursor()
    cur.execute("DELETE FROM article WHERE id = %s", (article_id,))
    if cur.rowcount == 0:
        # Article with the given ID not found
        raise HTTPException(status_code=404, detail="Article not found")
    conn.commit()
    cur.close()
    return {"message": f"Article {article_id} deleted successfully"}


# Run the API
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=1901)
