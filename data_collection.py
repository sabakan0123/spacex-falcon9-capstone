"""Demonstrate API and HTML collection without changing the analysis datasets."""
from pathlib import Path
import csv
import json
import re
import requests
from bs4 import BeautifulSoup

HERE = Path(__file__).resolve().parent
API_URL = 'https://api.spacexdata.com/v4/launches/past'
COURSE_SNAPSHOT = 'https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/API_call_spacex_api.json'
WIKI_URL = 'https://en.wikipedia.org/w/index.php?title=List_of_Falcon_9_and_Falcon_Heavy_launches&oldid=1027686922'
HEADERS = {'User-Agent': 'Mozilla/5.0 (educational SpaceX capstone project)'}

def collect_api():
    """Fetch the API when available; label the supplied course snapshot otherwise."""
    try:
        response = requests.get(API_URL, timeout=12, headers=HEADERS)
        response.raise_for_status()
        records = response.json()
        source = 'live SpaceX API'
    except requests.RequestException as exc:
        print(f'Live API unavailable ({type(exc).__name__}); using IBM course snapshot')
        response = requests.get(COURSE_SNAPSHOT, timeout=50)
        response.raise_for_status()
        records = response.json()
        source = 'IBM course static API-response snapshot'
    fields = ['flight_number', 'name', 'date_utc', 'rocket', 'success']
    with (HERE / 'api_launch_sample.csv').open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows({key: row.get(key) for key in fields} for row in records)
    print(f'{source}: {len(records)} launch records')

def scrape_wikipedia():
    """Extract visible launch rows from the course's fixed 2021 Wikipedia revision."""
    response = requests.get(WIKI_URL, timeout=50, headers=HEADERS)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    tables = soup.select('table.wikitable.plainrowheaders.collapsible')
    rows = []
    for table in tables:
        for row in table.select('tr'):
            cells = row.find_all(['th', 'td'], recursive=False)
            values = [re.sub(r'\s*\[\s*\w+\s*\]', '', c.get_text(' ', strip=True)).strip() for c in cells]
            if len(values) == 10 and values[0].isdigit():
                rows.append(values)
    headers = ['flight', 'date_time_utc', 'version_booster', 'launch_site', 'payload', 'payload_mass', 'orbit', 'customer', 'launch_outcome', 'booster_landing']
    with (HERE / 'wiki_launch_sample.csv').open('w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    print(f'Wikipedia revision 1027686922: {len(tables)} tables, {len(rows)} complete 10-column rows')

if __name__ == '__main__':
    collect_api()
    scrape_wikipedia()
