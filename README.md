# BrowserStack take-home

## Intent
The intention behind this readme is to mention why a certain approach was used, what went wrong for me to prioritise the approach and what were the tradeoffs, if any

## Scraper
Started local with plain Selenium and Chrome and fetched the first five links off /opinion/, with title and body text, saved the cover image for each. Following were some of the problems I encountered:

- When El País started throwing captchas, i realised this when I saw some blank articles. I kept debugging it as a selector problem until I realized it was PRISA Media's bot detection kicking in on repeated automated requests. So, I fixed it by hiding the automation flags navigator.webdriver, the automation extension switch, and setting a user agent, and adding randomized delays.

- Section pages were being added in as articles. A few of the articles turned out to be section fronts like /opinion/editoriales/, titled just "Opinión". to fix that, I added a filter for generic titles plus a dedupe check, and pulled from a buffer of 15 candidate URLs, so the scraper keeps going until it lands on 5 clean ones.

- Translation and word frequency were easy. I used deep translator to convert the five headers to English, then counted words repeated more than twice across all of them with collections.Counter.

- To verify images, I used manual rechecking ie; i opened each saved cover image to confirm they matched the right article and weren't broken.