import json

with open('page_info_full.json', 'r') as file:
    data = json.load(file)

total_count = len(data)
no_results_count = 0
no_h1 = 0
no_h1_urls = []
special_condition_count = 0
special_condition_urls = []

exclusion_keywords = ['swisslocationaward', '_eventlokale', '_redaktionell', 'extern', '_dienstleister']
excluded_url = "https://www.eventlokale.ch"

def is_excluded(url):
    return url == excluded_url or any(keyword in url for keyword in exclusion_keywords)

for entry in data:
    if entry.get('results_count') == "N/A":
        no_results_count += 1
        if not is_excluded(entry['url']):
            special_condition_count += 1
            special_condition_urls.append(entry['url'])
    if not entry.get('h1'):
        no_h1 += 1
        no_h1_urls.append(entry.get('url'))

results = {
    "total_count": total_count,
    "no_results_count": no_results_count,
    "no_h1_count": no_h1,
    "no_h1_urls": no_h1_urls,
    "special_condition_count": special_condition_count,
    "special_condition_urls": special_condition_urls
}

with open('page_info_count_results.json', 'w') as outfile:
    json.dump(results, outfile, indent=4)

print(f"Results saved to page_info_count_results.json")
