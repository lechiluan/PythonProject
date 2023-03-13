import json
import requests
import uvicorn
from fastapi import FastAPI
from parsel import Selector
from fastapi.responses import Response

app = FastAPI()


@app.get("/")
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
            # Make a GET request to fetch the raw HTML content
            try:
                link_request = requests.get(link)
            except requests.exceptions.ConnectionError:
                image_links = None
                content_descriptions = None
                contents = None
                hashtags = None
            else:
                if link_request.status_code == 200:
                    link_selector = Selector(text=link_request.text)
                    # get the link of the image, if it exists
                    image_links = link_selector.css("img[src*='jpg']::attr(src)").get()
                    # get the description of the news
                    content_descriptions = link_selector.css("meta[name='description']::attr(content)").get()
                    contents = link_selector.css("p::text").getall()
                    # get the hashtags
                    hashtags = link_selector.css("a[href*='hashtag']::text").getall()
                elif link_request.status_code == 404:
                    image_links = None
                    content_descriptions = None
                    contents = None
                    hashtags = None
                else:
                    image_links = None
                    content_descriptions = None
                    contents = None
                    hashtags = None

            data = {"rank": rank, "title": title, "link": link, "shortlink": short_link, "points": point,
                    "comments": comment, "time": time_post, "author": author, "image_link": image_links,
                    "content_description": content_descriptions,
                    "content": contents, "hashtag": hashtags}
            news_data.append(data)

        # Extract the next_id and n parameters for the next page (if available)
        next_link = selector.css("a.morelink::attr(href)").get()
        if next_link:
            next_id = next_link.split("=")[1].split("&")[0]
            n = next_link.split("=")[2]
    # format the data as JSON look at the JSON structure
    news_json = json.dumps(news_data, indent=4)

    # Write the JSON data to a file
    with open("news_data.json", "w") as f:
        json.dump(news_data, f)

    # Export the JSON-formatted string to a file and with timestamps.
    with open("news_data.json", "w") as f:
        f.write(news_json)

    # Return the JSON-formatted string as a response
    return Response(news_json, media_type="application/json")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=7000)
