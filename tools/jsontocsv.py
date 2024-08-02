import json
import csv

with open('page_info_full.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

csv_file = 'page_info_full.csv'

headers = data[0].keys()

with open(csv_file, 'w', newline='', encoding='utf-8') as file:
    csv_writer = csv.DictWriter(file, fieldnames=headers)
    csv_writer.writeheader()
    for row in data:
        csv_writer.writerow(row)

print(f"Data has been written to {csv_file}")
