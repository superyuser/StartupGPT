from pdfminer.high_level import extract_text
from bs4 import BeautifulSoup
import requests
import keyboard
import os
import mimetypes
import uuid
import re

DOWNLOAD_DIR = "data/downloads"
TARGET_DIR = "data/books"

def download(url):
    tag = re.sub(r'[<>:"/\\|?*]', '_', url.split('/')[-1] or "downloaded")
    if not tag:
        tag = "downloaded_" + str(uuid.uuid4())[:8]
    response = requests.get(url)
    content_type = response.headers.get("Content-Type", "")
    print(f"Content type: {content_type}")
    filetype = "pdf"
    extension = mimetypes.guess_extension(content_type.split(";")[0].strip())
    target_path = os.path.join(DOWNLOAD_DIR, f"{tag}{extension or '.bin'}")
    if "pdf" in content_type.lower():
        if not os.path.exists(DOWNLOAD_DIR):
            os.makedirs(DOWNLOAD_DIR)
        with open(target_path, "wb") as f:
            f.write(response.content)
        print(f"wrote to pdf @ {target_path}")
    elif "html" in content_type.lower():
        with open(target_path, "wb") as f:
            f.write(response.content)
        print(f"wrote to pdf @ {target_path}")
        filetype = "html"
    else:
        print("filetype unsupported!")
        filetype, tag, target_path = None, None, None
    return filetype, tag, target_path

def htmlToMD(html_path):
    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    text = soup.get_text()
    return text

# main
def linkToMD(url):
    filetype, tag, target = download(url)
    print(f"downloaded pdf to {target}!")
    text = None
    if filetype == "pdf":
        text = extract_text(target)
    elif filetype == "html":
        text = htmlToMD(target)
    else:
        print("filetype unsupported, skipping!")
        return
    want_tag = input("Enter filename: ")
    if not want_tag:
        want_tag = tag
    final_path = f"{TARGET_DIR}/{want_tag}.md"
    with open(final_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"converted to md @ {final_path}!")

def main():
    num_downloaded = 0
    while True:
        want_url = input("Enter url of pdf to download: ")
        if want_url == "q":
            break
        linkToMD(want_url)
        num_downloaded += 1
    print(f"saved {num_downloaded} to {TARGET_DIR}!")

if __name__ == "__main__":
    main()