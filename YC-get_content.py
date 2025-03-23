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

chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
driver = webdriver.Chrome(options = chrome_options)


TARGET_DIR = "data/books"

with open(".\YC_blog_links.txt", "r") as f:
    urls = [line.strip() for line in f]

def retrieve_one(url):
    driver.get(url)
    title = driver.find_element(By.CLASS_NAME, "ycdc-page-title").text
    body = driver.find_element(By.CSS_SELECTOR, ".prose.prose-sm.sm\\:prose-base.max-w-full").text
    return title, body

def save_to_md(urls):
    num_files = len(urls)
    for url in tqdm(urls):
        title, body = retrieve_one(url)
        title_to_save = title.replace(" ", "_")
        title_to_save = re.sub(r'[\\/*?:"<>|]', "", title_to_save)
        final_path = f"{TARGET_DIR}/YC_{title_to_save}.md"
        if not os.path.exists(final_path):
            with open(final_path, "w", encoding="utf-8") as f:
                f.write(body)
                print(f"🥳saved '{title}' @ {final_path}~")
        else:
            continue
    print(f"✨saved all {len(urls)} files to {TARGET_DIR}!")

if __name__ == "__main__":
    save_to_md(urls)
    driver.quit()