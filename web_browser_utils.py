# web_utils.py

import requests
from bs4 import BeautifulSoup
import re

def fetch_page_content(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract visible text
        visible_text = soup.get_text().strip()

        # Extract image descriptions
        image_descriptions = []
        images = soup.find_all('img')
        for img in images:
            alt_text = img.get('alt')
            if alt_text:
                image_descriptions.append(alt_text.strip())

        # Extract file links
        file_links = []
        file_elements = soup.find_all(['a', 'img'])
        for element in file_elements:
            href = element.get('href')
            src = element.get('src')
            if href and '.' in href.split('/')[-1]:
                file_links.append(href)
            elif src and '.' in src.split('/')[-1]:
                file_links.append(src)

        return visible_text, image_descriptions, file_links
    except Exception as e:
        print("Error while fetching page content:", e)
        return None, None, None

def main():
    # Test the fetch_page_content function with a sample URL
    url = 'https://en.wikipedia.org/wiki/Python_(programming_language)'
    visible_text, image_descriptions, file_links = fetch_page_content(url)
    print(f"Visible text:\n{visible_text}\n")
    print(f"Image descriptions:\n{image_descriptions}\n")
    print(f"File links:\n{file_links}\n")

if __name__ == '__main__':
    main()
