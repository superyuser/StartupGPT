import json
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from tqdm import tqdm
from time import sleep
import datetime
import re

url = "https://www.ycombinator.com/library/search?media_type=Blog"
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
driver = webdriver.Chrome()

BLOG_PATH = "YC_blog_links.txt"

def main():
    load_page()
    print("✅ page loaded")
    scroll_to_bottom()
    print("✅ scrolled to bottom")
    blogs = find_blogs()
    print("✅ found {} blog links".format(len(blogs)))
    populate_blogs(blogs)
    print(f"📝 wrote to {BLOG_PATH}!")
    driver.quit()

# load page -> see all options
def load_page():
    driver.get(url)
    sleep(2)

# scroll to bottom
def scroll_to_bottom():
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break # reached bottom
        last_height = new_height

    # find blocks
def find_blogs():
    blocks = driver.find_elements(
        By.CLASS_NAME, "_article_i9oky_350"
    )
    urls = [block.get_attribute("href") for block in blocks]
    print(f"🥳found blog links: {len(urls)}\n{urls}")
    return urls

def populate_blogs(urls):
    with open(BLOG_PATH, "a") as f:
        for url in urls:
            f.write(url + "\n")

if __name__ == "__main__":
    main()