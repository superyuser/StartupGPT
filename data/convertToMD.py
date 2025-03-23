from pdfminer.high_level import extract_text
import requests
import keyboard
import os
import mimetypes
import uuid
from bs4 import BeautifulSoup

DOWNLOAD_DIR = "./downloads"
TARGET_DIR = "./books"

def download(url):
    tag = url.split('/')[-1]
    if not tag:
        tag = "downloaded_" + str(uuid.uuid4())[:8]
    response = requests.get(url)
    content_type = response.headers.get("Content-Type", "")
    print(f"Content type: {content_type}")
    filetype = "pdf"
    if "pdf" in content_type.lower():
        if not os.path.exists(DOWNLOAD_DIR):
            os.makedirs(DOWNLOAD_DIR)
        target_path = f"{DOWNLOAD_DIR}/{tag}"
        with open(target_path, "wb") as f:
            f.write(response.content)
        print(f"wrote to pdf @ {target_path}")
    elif "html" in content_type.lower():
        target_path = f"{DOWNLOAD_DIR}/{tag}"
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

def pdfToMD(url):
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
    final_path = f"{TARGET_DIR}/{want_tag}.md"
    with open(final_path, "w") as f:
        f.write(text)
    print(f"converted to md @ {final_path}!")

def main():
    num_downloaded = 0
    while True:
        want_url = input("Enter url of pdf to download: ")
        if want_url == "q":
            break
        pdfToMD(want_url)
        num_downloaded += 1
    print(f"saved {num_downloaded} to {TARGET_DIR}!")

if __name__ == "__main__":
    main()