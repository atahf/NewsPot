import feedparser
import requests
import json
import os
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import concurrent.futures

rss_urls = (
    "https://www.ukrinform.net/rss/block-lastnews",         # ['id', 'guidislink', 'title', 'title_detail', 'links', 'link', 'summary', 'summary_detail', 'published', 'published_parsed', 'tags']
    "https://euromaidanpress.com/feed/",                    # ['title', 'title_detail', 'links', 'link', 'authors', 'author', 'author_detail', 'published', 'published_parsed', 'tags', 'id', 'guidislink', 'summary', 'summary_detail', 'content']
    "https://www.independent.co.uk/topic/ukraine/rss",      # ['title', 'title_detail', 'links', 'link', 'summary', 'summary_detail', 'published', 'published_parsed', 'id', 'guidislink', 'media_content', 'media_credit', 'credit', 'media_text', 'authors', 'author', 'author_detail', 'updated', 'updated_parsed', 'tags']
    "https://en.interfax.com.ua/news/last.rss",             # ['title', 'title_detail', 'links', 'link', 'summary', 'summary_detail', 'published', 'published_parsed', 'id', 'guidislink', 'tags']
    "https://unn.ua/rss/news_uk.xml",                       # ['title', 'title_detail', 'summary', 'summary_detail', 'links', 'link', 'id', 'guidislink', 'tags', 'published', 'published_parsed']
    "https://zn.ua/rss/full.rss",                           # ['title', 'title_detail', 'links', 'link', 'published', 'published_parsed', 'tags', 'summary', 'summary_detail', 'content']
)

def crawl(rss_url, crawled_news):
    rss_feed = feedparser.parse(rss_url)
    for entry in rss_feed.entries:
        try:
            imgs = []
            for elem in entry.links:
                if "image" in elem.type and "www" in elem.href:
                    imgs.append(elem.href)
            if rss_url == rss_urls[0] and entry.link:
                response = requests.get(entry.link)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")
                    container = soup.find("div", class_="newsText")
                    divs = container.find_all("div", recursive=False)
                    article = divs[1]
                    for child in article.find_all(recursive=False):
                        if child.name != 'p':
                            child.extract()
                    p_tags = article.find_all("p")
                    text = " ".join(t.get_text() for t in p_tags if len(t.get_text()) > 0 and t.get_text() != "Read also:")
                    crawled_news["result"] += 1
                    crawled_news["data"].append({
                        "id": crawled_news["result"],
                        "title": entry.get("title", ""),
                        "link": entry.get("link", ""),
                        "content": text,
                        "published": entry.get("published", ""),
                        "images": imgs
                    })
            elif rss_url == rss_urls[1] and entry.link:
                response = requests.get(entry.link)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")
                    article = soup.find("div", class_="entry-content")
                    for child in article.find_all(recursive=False):
                        if child.name != 'p':
                            child.extract()
                    p_tags = article.find_all("p")
                    text = " ".join(t.get_text() for t in p_tags if len(t.get_text()) > 0 and t.get_text() != "Read also:")
                    crawled_news["result"] += 1
                    crawled_news["data"].append({
                        "id": crawled_news["result"],
                        "title": entry.get("title", ""),
                        "link": entry.get("link", ""),
                        "content": text,
                        "published": entry.get("published", ""),
                        "images": imgs
                    })
            elif rss_url == rss_urls[2] and entry.link and "https://www.independent.co.uk/tv/" not in entry.link:
                response = requests.get(entry.link)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")
                    article = soup.find("div", id="main")
                    for child in article.find_all(recursive=False):
                        if child.name != 'p':
                            child.extract()
                    p_tags = article.find_all("p")
                    text = " ".join(t.get_text() for t in p_tags if len(t.get_text()) > 0)
                    crawled_news["result"] += 1
                    crawled_news["data"].append({
                        "id": crawled_news["result"],
                        "title": entry.get("title", ""),
                        "link": entry.get("link", ""),
                        "content": text,
                        "published": entry.get("published", ""),
                        "images": imgs
                    })
            elif rss_url == rss_urls[3] and entry.link:
                response = requests.get(entry.link)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")
                    article = soup.find("div", class_="article-content")
                    for child in article.find_all(recursive=False):
                        if child.name != 'p':
                            child.extract()
                    p_tags = article.find_all("p")
                    text = " ".join(t.get_text() for t in p_tags if len(t.get_text()) > 0)
                    crawled_news["result"] += 1
                    crawled_news["data"].append({
                        "id": crawled_news["result"],
                        "title": entry.get("title", ""),
                        "link": entry.get("link", ""),
                        "content": text,
                        "published": entry.get("published", ""),
                        "images": imgs
                    })
            elif rss_url == rss_urls[4] and entry.link:
                response = requests.get(entry.link)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")
                    article = soup.find("div", class_="single-news-card_body__xHoem")
                    for child in article.find_all(recursive=False):
                        if child.name != 'p':
                            child.extract()
                    p_tags = article.find_all("p")
                    text = " ".join(t.get_text() for t in p_tags if len(t.get_text()) > 0)
                    crawled_news["result"] += 1
                    crawled_news["data"].append({
                        "id": crawled_news["result"],
                        "title": entry.get("title", ""),
                        "link": entry.get("link", ""),
                        "content": text,
                        "published": entry.get("published", ""),
                        "images": imgs
                    })
            elif rss_url == rss_urls[5] and entry.link:
                response = requests.get(entry.link)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")
                    article = soup.find("div", class_="content-wrap-inside")
                    for child in article.find_all(recursive=False):
                        if child.name != 'p':
                            child.extract()
                    p_tags = article.find_all("p")
                    text = " ".join(t.get_text() for t in p_tags if len(t.get_text()) > 0)
                    crawled_news["result"] += 1
                    crawled_news["data"].append({
                        "id": crawled_news["result"],
                        "title": entry.get("title", ""),
                        "link": entry.get("link", ""),
                        "content": text,
                        "published": entry.get("published", ""),
                        "images": imgs
                    })
        except Exception as e:
            continue

def crawl_news():
    crawled_news = {
        "result": 0,
        "last_update": datetime.now().isoformat(),
        "data": []
    }

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_results = [executor.submit(crawl, URL, crawled_news) for URL in rss_urls]
        concurrent.futures.wait(future_results)
        

        with open("news.json", 'w', encoding="utf-8") as f:
            json.dump(crawled_news, f, ensure_ascii=False, indent=4)

def get_news(h=0, m=0, s=0, recursive=False):
    if os.path.exists("news.json"):
        with open("news.json", 'r', encoding="utf-8") as f:
            res = json.load(f)
        if res:
            update_interval = timedelta(hours=h, minutes=m, seconds=s)
            last_update = datetime.strptime(res["last_update"], "%Y-%m-%dT%H:%M:%S.%f")
            if (datetime.now() - last_update) < update_interval:
                del res["last_update"]
                return res, recursive
    
    crawl_news()
    return get_news(h=h, m=m, s=s, recursive=True)
