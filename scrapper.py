from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import os
import time
import random

OPINION_URL = "https://elpais.com/opinion/"
GENERIC_TITLES = {"opinión", "opinion", "editoriales", "tribunas"}

def get_local_driver():
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument(
        "user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
    driver = webdriver.Chrome(options=options)
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"}
    )
    return driver

def accept_cookies(driver):
    try:
        driver.find_element(By.ID, "didomi-notice-agree-button").click()
        time.sleep(1)
    except Exception:
        pass

def is_blocked(driver):
    page_source = driver.page_source.lower()
    return "verification required" in page_source or "slide right to secure" in page_source

def scrape_opinion_articles(driver, limit=5, save_images=True, image_dir="images", url_buffer=15):
    driver.get(OPINION_URL)
    accept_cookies(driver)
    time.sleep(random.uniform(1.5, 3))

    links = driver.find_elements(By.CSS_SELECTOR, "article a")
    candidate_urls = []
    for link in links:
        href = link.get_attribute("href")
        if href and href not in candidate_urls and "/opinion/" in href:
            candidate_urls.append(href)
        if len(candidate_urls) >= url_buffer:
            break

    articles = []
    seen_titles = set()
    if save_images:
        os.makedirs(image_dir, exist_ok=True)

    for url in candidate_urls:
        if len(articles) >= limit:
            break

        driver.get(url)
        time.sleep(random.uniform(1.5, 3.5))

        if is_blocked(driver):
            print(f"skipping cause blocked: {url}")
            continue

        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "h1"))
            )
        except Exception:
            print(f"skipping cause no h1: {url}")
            continue

        h1_elements = driver.find_elements(By.CSS_SELECTOR, "h1")
        title = h1_elements[0].text.strip() if h1_elements else None

        if not title:
            print(f"skipping empty title: {url}")
            continue

        if title.lower() in GENERIC_TITLES:
            print(f"skipping generic: {url}")
            continue

        if title in seen_titles:
            print(f"skipping same totle: {url}")
            continue

        paragraphs = driver.find_elements(By.CSS_SELECTOR, "article p")
        content = "\n".join(p.text for p in paragraphs if p.text.strip())
        if not content:
            print(f"skipping cause it has nothing: {url}")
            continue

        image_path = None
        if save_images:
            imgs = driver.find_elements(By.CSS_SELECTOR, "article img")
            if imgs:
                img_url = imgs[0].get_attribute("src")
                if img_url:
                    image_path = os.path.join(image_dir, f"article_{len(articles)+1}.jpg")
                    try:
                        resp = requests.get(img_url, timeout=10)
                        with open(image_path, "wb") as f:
                            f.write(resp.content)
                    except Exception:
                        image_path = None

        print(f"[{len(articles)+1}] ok: {title}\n{content[:200]}...\n")
        seen_titles.add(title)
        articles.append({"url": url, "title": title, "content": content, "image_path": image_path})

    if len(articles) < limit:
        print(f"only got {len(articles)} articles out of {limit}")

    return articles