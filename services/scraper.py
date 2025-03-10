import asyncio
import requests
import html2text
from bs4 import BeautifulSoup
from concurrent.futures import ProcessPoolExecutor
from config import SEARXNG_URL_BASE_URL

def get_search_results(query):
    print(f"Querying for {query}")
    query_params = {
        "q": query,
        "safesearch": "0",
        "format": "json",
        "language": "en",
        "engines": "google",
    }
    out = requests.get(f"{SEARXNG_URL_BASE_URL}search", params=query_params)
    out_json = out.json()
    result_links = [i['url'] for i in out_json['results'][:5]]
    print(f"Result link count {len(result_links)}")
    return result_links

h = html2text.HTML2Text()
h.ignore_links = True
h.ignore_images = True

def retrieve_page_content(url):
    print(f"retrieving page content for {url}")
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
            "Referer": "https://www.google.com/",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "identity"
        }
        page = requests.get(url, headers=headers, timeout=15)
        page.raise_for_status()
        soup = BeautifulSoup(page.content, "html.parser")
        html_content = str(soup)
        #markdown = html2text.html2text(html_content)
        markdown = h.handle(html_content)

    except requests.exceptions.Timeout:
        print(f"Timeout occurred for {url}")
        return {"url":url,"markdown":""}
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {url} :: {e}")
        return {"url":url,"markdown":""}
    return {"url":url,"markdown":markdown}

def query_result_retriever(query):
    urls = get_search_results(query)
    results = []
    with ProcessPoolExecutor() as executor:
        results = list(executor.map(retrieve_page_content, urls))
    return results

