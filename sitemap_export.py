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
        thread_local.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
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

def main(sitemap_url, output_file, max_count=None, batch_size=100):
    sitemap_urls = get_sitemap_urls(sitemap_url)
    all_sitemap_urls = []
    
    for url in sitemap_urls:
        sub_sitemap_urls = get_sitemap_urls(url)
        all_sitemap_urls.extend(sub_sitemap_urls)
    
    if max_count:
        all_sitemap_urls = all_sitemap_urls[:max_count]
    
    total_urls = len(all_sitemap_urls)
    batches = [all_sitemap_urls[i:i + batch_size] for i in range(0, total_urls, batch_size)]
    
    all_page_info = []
    for i, batch in enumerate(batches):
        print(f"Processing batch {i + 1}/{len(batches)}")
        batch_info = process_sitemap_urls(batch)
        all_page_info.extend(batch_info)
        
        temp_output_file = f"{output_file}_batch_{i + 1}.json"
        with open(temp_output_file, 'w', encoding='utf-8') as f:
            json.dump(batch_info, f, ensure_ascii=False, indent=4)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_page_info, f, ensure_ascii=False, indent=4)

    print("Data has been successfully extracted and saved to", output_file)

sitemap_url = 'https://www.eventlokale.ch/sitemap.xml'
output_file = 'page_info.json'
max_count = None
main(sitemap_url, output_file, max_count)
