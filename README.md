# BrowserStack take-home

## Intent
The intention behind this readme is to mention why a certain approach was used, what went wrong for me to prioritise the approach and what were the tradeoffs, if any

## Scraper
i started local with plain Selenium and Chrome and fetched the first five links from /opinion/, with title and body text, saved the cover image for each. Following were some of the problems I encountered:

- When El País started throwing captchas, i realised this when I saw some blank articles. I kept debugging it as a selector problem until I realized it was PRISA Media's bot detection kicking in on repeated automated requests. So, I fixed it by hiding the automation flags navigator.webdriver, the automation extension switch, and setting a user agent, and adding randomized delays.

- Section pages were being added in as articles. A few of the articles turned out to be section fronts like /opinion/editoriales/, titled just "Opinión". to fix that, I added a filter for generic titles plus a dedupe check, and pulled from a buffer of 15 candidate URLs, so the scraper keeps going until it lands on 5 clean ones.

- Translation and word frequency were easy. I used deep translator to convert the five headers to English, then counted words repeated more than twice across all of them with collections.Counter.

- To verify images, I used manual rechecking ie; i opened each saved cover image to confirm they matched the right article and weren't broken.

## Issues

After I moved from local scraping to running the same logic on BrowserStack, I ran into a lot of issues, like:

- First issue was timeouts as running all 5 configs in parallel caused 5 threads hitting El País at once, which made the bot detection trigger way more than it did locally.

- To cut down, I trimmed all threads down to just 1 article instead of 5 since the point of this part was proving cross browser execution works. i also added a hard 90s timeout per thread with ThreadPoolExecutor so a stuck session doesn't hang.

- All runs were also landing in the same "Untitled Build Run" on BrowserStack and not creating a fresh one, since I wasn't passing a build name. I fixed that by generating a timestamped buildName at runtime.

-  The instability only was under full concurrency, so from here it's about scaling that isolated success back up to all 5 configs without triggering the bot detection.

## Final notes

in the end, the concurrency instability wasn't fully a code problem. After tuning worker count, buffer size, and stagger timing and still seeing every run fail with "Automate testing time expired", I checked my plan usage and found the free Automate trial's 100 minutes were used up from all the earlier debugging runs. So i created another trial account, added the new credentials into .env, and the same code ran with 5/5 passed on the first real attempt.


## Discards

I'd created a static/index.html file to have a dashboard with a html table, but seemed of no use so had to discard that