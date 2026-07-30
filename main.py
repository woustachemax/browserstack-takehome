from scrapper import get_local_driver, scrape_opinion_articles
from translator import translate_titles, find_repeated_words
from browserstack import run_all
import threading
import uvicorn

def main():
    driver = get_local_driver()
    articles = scrape_opinion_articles(driver)
    driver.quit()

    valid_articles = [a for a in articles if a["title"] != "N/A"]

    titles = [a["title"] for a in valid_articles]
    translated = translate_titles(titles)
    for orig, eng in zip(titles, translated):
        print(f"{orig} -> {eng}")

    repeated = find_repeated_words(translated)
    print("Repeated words:", repeated)

    threading.Thread(target=run_all, daemon=True).start()
    uvicorn.run("dashboard:app", host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()