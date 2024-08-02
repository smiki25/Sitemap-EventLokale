import json
import requests
from bs4 import BeautifulSoup

def get_sitemap_urls(sitemap_url):
    response = requests.get(sitemap_url, timeout=20)
    soup = BeautifulSoup(response.content, 'xml')
    return [loc.text for loc in soup.find_all('loc')]

def filter_search_urls(urls):
    return [url for url in urls if 'search_' in url]

def load_json(json_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data, json_file):
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def main(sitemap_url, page_info_file, output_file):
    sitemap_urls = get_sitemap_urls(sitemap_url)
    search_urls = filter_search_urls(sitemap_urls)
    
    all_search_urls = []
    for url in search_urls:
        sub_sitemap_urls = get_sitemap_urls(url)
        all_search_urls.extend(sub_sitemap_urls)
    
    page_info = load_json(page_info_file)
    filtered_page_info = [entry for entry in page_info if entry['url'] in all_search_urls]
    
    save_json(filtered_page_info, output_file)
    print(f"Filtered data has been saved to {output_file}")

sitemap_url = 'https://www.eventlokale.ch/sitemap.xml'
page_info_file = 'page_info_full.json'
output_file = 'filtered_page_info.json'

main(sitemap_url, page_info_file, output_file)
