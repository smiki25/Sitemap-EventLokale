import json
import re
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import os

thread_local = threading.local()

def get_driver():
    if not hasattr(thread_local, "driver"):
        thread_local.driver = webdriver.Chrome()
    return thread_local.driver

def get_sitemap_urls(sitemap_url):
    response = requests.get(sitemap_url, timeout=20)
    soup = BeautifulSoup(response.content, 'xml')
    return [loc.text for loc in soup.find_all('loc')]

def filter_search_urls(urls):
    return [url for url in urls if 'search_' in url]

def get_page_info(url):
    driver = get_driver()

    driver.set_page_load_timeout(20) 

    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'h1, .search-page__header__title, .sla-2023-total-items'))
        )
        
        if driver.title == "404 Not Found":
            raise Exception("404 Not Found")

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        h1_tag = soup.find('h1', id='search-page__header__title')
        if not h1_tag:
            h1_tag = soup.find('h1', class_='search-page__header__title')
        if not h1_tag:
            h1_tag = soup.select_one('a[href] h1')
        if not h1_tag:
            h1_tag = soup.find('h1')
        h1_text = h1_tag.get_text(strip=True) if h1_tag else 'N/A'
        
        result_count_tag = soup.find('span', class_='search-page__header__count')
        if not result_count_tag:
            result_count_tag = soup.find('p', class_='sla-2023-total-items')
        result_count_text = result_count_tag.get_text(strip=True) if result_count_tag else 'N/A'
        
        if result_count_text == 'N/A':
            try:
                result_count_element = driver.find_element(By.CLASS_NAME, 'sla-2023-total-items')
                result_count_text = result_count_element.get_attribute("textContent").strip()
            except Exception as e:
                print(f"Error fetching result count for {url}: {e}")
        
        return {
            'url': url,
            'h1': h1_text,
            'results_count': result_count_text
        }
    except Exception as e:
        print(f"Error processing {url}: {e}")
        driver.quit()
        thread_local.driver = webdriver.Chrome()
        return {
            'url': url,
            'h1': 'Error',
            'results_count': 'Error'
        }

def process_sitemap_urls(sitemap_urls):
    all_page_info = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_url = {executor.submit(get_page_info, url): url for url in sitemap_urls}
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                page_info = future.result()
                all_page_info.append(page_info)
                print(f"Processed: {url}")
            except Exception as e:
                print(f"Error fetching {url}: {e}")
    return all_page_info

def main(sitemap_url, page_info_file, output_file, max_count=None, batch_size=350):
    # Load the existing JSON data
    page_info_file_path = os.path.join('..', 'json', page_info_file)
    with open(page_info_file_path, 'r', encoding='utf-8') as file:
        page_info_data = json.load(file)

    # Filter entries with "h1" or "results_count" equal to "Missing due to error"
    error_entries = [entry for entry in page_info_data if entry['h1'] == "Missing due to error" or entry['results_count'] == "Missing due to error"]
    error_urls = [entry['url'] for entry in error_entries]

    if error_entries:
        print(f"Found {len(error_entries)} entries with errors. Re-fetching their information...")
        error_page_info = process_sitemap_urls(error_urls)

        # Update the original page info data with the corrected entries
        for updated_entry in error_page_info:
            for entry in page_info_data:
                if entry['url'] == updated_entry['url']:
                    entry['h1'] = updated_entry['h1']
                    entry['results_count'] = updated_entry['results_count']

    # Save the updated data
    output_file_path = os.path.join('..', 'json', output_file)
    with open(output_file_path, 'w', encoding='utf-8') as f:
        json.dump(page_info_data, f, ensure_ascii=False, indent=4)

    print("Data has been successfully updated and saved to", output_file)

sitemap_url = 'https://www.eventlokale.ch/sitemap.xml'
page_info_file = 'updated_page_info.json'
output_file = 'updated_page_info_with_missing.json'
max_count = None
main(sitemap_url, page_info_file, output_file, max_count)
