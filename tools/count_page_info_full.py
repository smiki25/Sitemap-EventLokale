import json
import os
from collections import Counter

# Define the relative paths to the JSON files
filtered_page_info_path = os.path.join('..', 'json', 'updated_page_info.json')
output_path = os.path.join('..', 'json', 'updated_page_info_count_results.json')

# Load the JSON data from the file
with open(filtered_page_info_path, 'r') as file:
    data = json.load(file)

total_count = len(data)
no_results_count = 0
no_h1 = 0
no_h1_urls = []
special_condition_count = 0
special_condition_urls = []
duplicate_count = 0
duplicate_urls = []

exclusion_keywords = ['swisslocationaward', '_eventlokale', '_redaktionell', 'extern', '_dienstleister']
excluded_url = "https://www.eventlokale.ch"

def is_excluded(url):
    return url == excluded_url or any(keyword in url for keyword in exclusion_keywords)

url_counter = Counter(entry['url'] for entry in data)
duplicates = [url for url, count in url_counter.items() if count > 1]

for entry in data:
    if entry.get('results_count') == "N/A":
        no_results_count += 1
        if not is_excluded(entry['url']):
            special_condition_count += 1
            special_condition_urls.append(entry['url'])
    if not entry.get('h1'):
        no_h1 += 1
        no_h1_urls.append(entry.get('url'))

duplicate_count = len(duplicates)
duplicate_urls = duplicates

results = {
    "total_count": total_count,
    "no_results_count": no_results_count,
    "no_h1_count": no_h1,
    "no_h1_urls": no_h1_urls,
    "special_condition_count": special_condition_count,
    "special_condition_urls": special_condition_urls,
    "duplicate_count": duplicate_count,
    "duplicate_urls": duplicate_urls
}

with open(output_path, 'w') as outfile:
    json.dump(results, outfile, indent=4)

print(f"Results saved to {output_path}")
