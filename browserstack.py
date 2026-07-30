import os
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from scrapper import scrape_opinion_articles
from status import set_status

load_dotenv()

BS_USERNAME = os.environ.get("BROWSERSTACK_USERNAME")
BS_ACCESS_KEY = os.environ.get("BROWSERSTACK_ACCESS_KEY")
BS_URL = f"https://{BS_USERNAME}:{BS_ACCESS_KEY}@hub-cloud.browserstack.com/wd/hub"

BUILD_NAME = f"Build Run {time.strftime('%Y-%m-%d %H:%M:%S')}"
print(f"Using build name: {BUILD_NAME}")
CONFIGS = [
    {"browserName": "Chrome", "bstack:options": {"os": "Windows", "osVersion": "11", "sessionName": "chrome-win"}},
    {"browserName": "Firefox", "bstack:options": {"os": "Windows", "osVersion": "11", "sessionName": "firefox-win"}},
    {"browserName": "Safari", "bstack:options": {"os": "OS X", "osVersion": "Sonoma", "sessionName": "safari-mac"}},
    {"browserName": "Chrome", "bstack:options": {"deviceName": "Samsung Galaxy S23", "realMobile": "true", "sessionName": "chrome-android"}},
    {"browserName": "Safari", "bstack:options": {"deviceName": "iPhone 14", "realMobile": "true", "sessionName": "safari-ios"}},
]

def run_on_config(config):
    name = config["bstack:options"]["sessionName"]
    set_status(name, "running")
    options = ChromeOptions()
    bstack_opts = dict(config["bstack:options"])
    bstack_opts["buildName"] = BUILD_NAME
    bstack_opts["sessionName"] = name
    options.set_capability("bstack:options", bstack_opts)
    options.set_capability("browserName", config["browserName"])
    driver = None
    try:
        driver = webdriver.Remote(command_executor=BS_URL, options=options)
        scrape_opinion_articles(driver, limit=1, save_images=False, url_buffer=10)
        set_status(name, "passed")
    except Exception as e:
        set_status(name, f"failed: {e}")
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass

def run_all():
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {}
        for config in CONFIGS:
            futures[executor.submit(run_on_config, config)] = config
            time.sleep(3)

        for future, config in futures.items():
            name = config["bstack:options"]["sessionName"]
            try:
                future.result(timeout=120)
            except FutureTimeoutError:
                set_status(name, "failed: timed out after 120s")

# from status import get_status

if __name__ == "__main__":
    run_all()