from deep_translator import GoogleTranslator
from collections import Counter
import re

def translate_titles(titles):
    return [GoogleTranslator(source="es", target="en").translate(t) for t in titles]

def find_repeated_words(translated_titles, min_count=2):
    words = []
    for title in translated_titles:
        words.extend(re.findall(r"[a-zA-Z']+", title.lower()))
    counts = Counter(words)
    return {w: c for w, c in counts.items() if c > min_count}