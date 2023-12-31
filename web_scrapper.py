
pip install markdownify bs4

import requests
from bs4 import BeautifulSoup
import json
import markdownify
import os

base_url = input("Enter the url to scrape:: ")

def clean_text(text):
  soup = BeautifulSoup(text, 'html.parser')

  unwanted_classes = ["sidebar-class", "social-media-class"]
  unwanted_tags = ["script", "style", "iframe"]

  for tag in soup.find_all(class_=unwanted_classes):
      tag.extract()

  for tag in soup.find_all(unwanted_tags):
      tag.extract()


  cleaned_text = soup.get_text()

  cleaned_text = ' '.join(cleaned_text.split())
  return text

def scrape_page(url):
    response = requests.get(url,timeout=5)
    soup = BeautifulSoup(response.content, 'html.parser')

    try:

        title = soup.find('title').text

        content = soup.find(id='content')
        if content:
            content_text = clean_text(content.text)
        else:
            content_text = "Content not found on this page."


        tables = content.find_all('table')
        for table in tables:
            markdown_table = markdownify.markdownify(str(table))
            table.replace_with(BeautifulSoup(markdown_table, 'html.parser'))

        return {'title': title, 'content': content_text}
    except Exception as e:

        print(f"Error scraping page: {url}")
        print(f"Exception: {e}")
        return {'title': 'Error', 'content': 'Error scraping this page.'}

def get_total_pages(base_url):
    response = requests.get(base_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    page_links = soup.find_all('a', class_='page-numbers')
    if page_links:
        return len(page_links)
    else:
        return 1

def scrape_new_pages(base_url, num_pages, data_dir):
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    existing_data = []
    scraped_urls = set()

    data_file = os.path.join(data_dir, 'scraped_data.json')
    if os.path.exists(data_file):
        with open(data_file, 'r') as json_file:
            existing_data = json.load(json_file)
            scraped_urls = set(item['url'] for item in existing_data)

    total_pages = get_total_pages(base_url)
    num_pages_to_scrape = min(num_pages, total_pages)

    new_data = []
    for page_num in range(1, num_pages_to_scrape + 1):
        page_url = f"{base_url}?page={page_num}"

        if page_url in scraped_urls:
            print(f"Skipping already scraped URL: {page_url}")
            continue

        page_data = scrape_page(page_url)
        page_data['url'] = page_url

        new_data.append(page_data)
        scraped_urls.add(page_url)

    all_data = existing_data + new_data if existing_data else new_data
    with open(data_file, 'w') as json_file:
        json.dump(all_data, json_file, indent=4)

scrape_new_pages(base_url, num_pages=5, data_dir='data')

