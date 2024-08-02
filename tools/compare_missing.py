import json
import os
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
    # Get all sitemap URLs
    sitemap_urls = get_sitemap_urls(sitemap_url)
    # Filter URLs that contain 'search_'
    search_urls = filter_search_urls(sitemap_urls)
    
    # Get all URLs from the search URLs' sub-sitemaps
    all_search_urls = []
    for url in search_urls:
        sub_sitemap_urls = get_sitemap_urls(url)
        all_search_urls.extend(sub_sitemap_urls)
    
    # Load existing page info from JSON file
    page_info = load_json(page_info_file)
    
    # Extract URLs from page info
    page_info_urls = [entry['url'] for entry in page_info]
    
    # Identify URLs present in all_search_urls but missing in page_info_urls
    missing_urls = set(all_search_urls) - set(page_info_urls)
    
    # Add missing URLs to the page_info list
    for url in missing_urls:
        page_info.append({
            "url": url,
            "h1": "Missing due to error",  # Placeholder, adjust as necessary
            "results_count": "Missing due to error"  # Placeholder, adjust as necessary
        })
    
    # Save the updated page info to the output file
    save_json(page_info, output_file)
    print(f"Updated data has been saved to {output_file}")

sitemap_url = 'https://www.eventlokale.ch/sitemap.xml'
page_info_file = os.path.join('..', 'json', 'updated_page_info_with_missing.json')
output_file = os.path.join('..', 'json', 'updated_page_info.json')

main(sitemap_url, page_info_file, output_file)
