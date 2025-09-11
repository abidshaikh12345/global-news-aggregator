from flask import Flask, render_template, request, redirect, url_for
import requests
import feedparser

app = Flask(__name__)

# Your Mediastack API Key
API_KEY = "e73aec3f7db74844d4e0bba97e876434"

# List of countries
COUNTRIES = {
    "India": "in",
    "United States": "us",
    "United Kingdom": "gb",
    "Canada": "ca",
    "Australia": "au",
    "Germany": "de",
    "France": "fr",
    "Japan": "jp",
    "China": "cn",
    "Brazil": "br",
    "South Africa": "za",
    "Russia": "ru",
    "Italy": "it",
    "Mexico": "mx",
    "Saudi Arabia": "sa"
}

# Store community articles
community_articles = []

# Example RSS feeds
RSS_FEEDS = {
    "global": "http://rss.cnn.com/rss/edition.rss",
    "india": "https://timesofindia.indiatimes.com/rssfeeds/296589292.cms"
}


@app.route("/")
def home():
    country = request.args.get("country", "in")
    url = f"http://api.mediastack.com/v1/news?access_key={API_KEY}&countries={country}&limit=30&sort=published_desc"
    response = requests.get(url)
    data = response.json()
    articles = data.get("data", [])

    # ✅ Remove duplicates (based on title)
    seen = set()
    unique_articles = []
    for a in articles:
        if a["title"] not in seen:
            unique_articles.append(a)
            seen.add(a["title"])

    # Split API news into with/without images
    api_with_images = [a for a in unique_articles if a.get("image")]
    api_without_images = [a for a in unique_articles if not a.get("image")]

    # Trending = first 3 API articles with images
    trending = api_with_images[:3]

    # RSS news
    rss_feed = feedparser.parse(RSS_FEEDS["global"])
    rss_articles = []
    for entry in rss_feed.entries[:5]:
        rss_articles.append({
            "title": entry.title,
            "description": entry.summary if "summary" in entry else "",
            "url": entry.link,
            "image": None
        })

    # Latest = API with images (excluding trending) + RSS + API without images
    latest = api_with_images[3:] + rss_articles + api_without_images

    return render_template("index.html",
                           trending=trending,
                           articles=latest,
                           countries=COUNTRIES,
                           country=country)


@app.route("/submit", methods=["GET", "POST"])
def submit():
    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        url = request.form["url"]

        article = {
            "title": title,
            "description": description,
            "url": url,
            "image": None
        }
        community_articles.append(article)
        return redirect(url_for("community"))

    return render_template("submit.html")


@app.route("/community")
def community():
    return render_template("community.html", articles=community_articles)


if __name__ == "__main__":
    app.run(debug=True)
