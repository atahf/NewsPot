import feedparser
import requests
import json
import os
from datetime import datetime, timedelta

rss_urls = (
    "https://www.ukrinform.net/rss/block-lastnews",         # ['id', 'guidislink', 'title', 'title_detail', 'links', 'link', 'summary', 'summary_detail', 'published', 'published_parsed', 'tags']
    "https://euromaidanpress.com/feed/",                    # ['title', 'title_detail', 'links', 'link', 'authors', 'author', 'author_detail', 'published', 'published_parsed', 'tags', 'id', 'guidislink', 'summary', 'summary_detail', 'content']
    "https://www.independent.co.uk/topic/ukraine/rss",      # ['title', 'title_detail', 'links', 'link', 'summary', 'summary_detail', 'published', 'published_parsed', 'id', 'guidislink', 'media_content', 'media_credit', 'credit', 'media_text', 'authors', 'author', 'author_detail', 'updated', 'updated_parsed', 'tags']
    "https://en.interfax.com.ua/news/last.rss",             # ['title', 'title_detail', 'links', 'link', 'summary', 'summary_detail', 'published', 'published_parsed', 'id', 'guidislink', 'tags']
    "https://unn.ua/rss/news_uk.xml",                       # ['title', 'title_detail', 'summary', 'summary_detail', 'links', 'link', 'id', 'guidislink', 'tags', 'published', 'published_parsed']
)

def crawl_news():
    crawled_news = {
        "result": 0,
        "last_update": datetime.now().isoformat(),
        "data": []
    }

    for rss_url in rss_urls:
        rss_feed = feedparser.parse(rss_url)
        for entry in rss_feed.entries:
            crawled_news["result"] += 1
            crawled_news["data"].append({
                "id": crawled_news["result"],
                "title": entry.get("title", ""),
                "link": entry.get("link", ""),
                "summary": entry.get("summary", ""),
                "published": entry.get("published", ""),
            })

    with open("news.json", 'w') as f:
        json.dump(crawled_news, f, ensure_ascii=False, indent=4)

def get_news(h=0, m=0, s=0, recursive=False):
    if os.path.exists("news.json"):
        with open("news.json", 'r') as f:
            res = json.load(f)
        if res:
            update_interval = timedelta(hours=h, minutes=m, seconds=s)
            last_update = datetime.strptime(res["last_update"], "%Y-%m-%dT%H:%M:%S.%f")
            if (datetime.now() - last_update) < update_interval:
                del res["last_update"]
                return res, recursive
    
    crawl_news()
    return get_news(h=h, m=m, s=s, recursive=True)
