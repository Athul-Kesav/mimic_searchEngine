import math
import re
from collections import defaultdict, Counter
from pymongo import MongoClient
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

# Setup
nltk.download('stopwords')
STOPWORDS = set(stopwords.words('english'))

print("[Connecting] to DB")
client = MongoClient("mongodb://localhost:27017/")
db = client["search_engine"]
pages_col = db["pages"]
index_col = db["inverted_index"]
print("[Established] connection")

# Tokenizer with better cleanup
def tokenize(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    tokens = text.split()
    return [
        t for t in tokens 
        if t not in STOPWORDS and len(t) > 2 and not any(char.isdigit() for char in t)
    ]

# Multithreaded fetch using requests
HEADERS = {"User-Agent": "Mozilla/5.0"}

def fetch(link):
    try:
        res = requests.get(link, headers=HEADERS, timeout=8)
        soup = BeautifulSoup(res.text, 'lxml')
        return link, soup.get_text(separator=' ')
    except Exception as e:
        print(f"[Error fetching] {link}: {e}")
        return link, ""

# Needed ChatGPT for this section

def fetch_all(links, max_workers=32):
    output_texts = {}
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(fetch, link): link for link in links}
        for future in as_completed(futures):
            link, text = future.result()
            output_texts[link] = text
    return output_texts

# Step 1: Fetch pages
n = 100  # Number of pages
docs = list(pages_col.find({}, {"link": 1}).limit(n))
links = [d['link'] for d in docs]

output_texts = fetch_all(links)
print(f"[Done] Downloaded {len(output_texts)} pages.")

# Step 2: Tokenize + Count
doc_word_counts = {}
doc_lengths = {}
df = defaultdict(int)

for link, text in output_texts.items():
    tokens = tokenize(text)
    wc = Counter(tokens)
    if not wc:
        continue
    doc_word_counts[link] = wc
    doc_lengths[link] = sum(wc.values())
    for word in wc:
        df[word] += 1

total_docs = len(doc_word_counts)
print("[Stats] Total docs with tokens:", total_docs)
print("[Stats] Total unique tokens:", len(df))

# Step 3: Compute TF-IDF and insert one-by-one
for word, doc_freq in df.items():
    idf = math.log(total_docs / doc_freq)
    postings = []

    for link, wc in doc_word_counts.items():
        if word in wc:
            tf = wc[word] / doc_lengths[link]
            tfidf = tf * idf
            postings.append({
                "link": link,
                "tf": round(tf, 6),
                "tfidf": round(tfidf, 6)
            })

    if postings:
        existing = index_col.find_one({"word": word}, {"docs": 1})
        old_docs = existing.get("docs", []) if existing else []
        old_docs_map = {d["link"]: d for d in old_docs}

        for p in postings:
            old_docs_map[p["link"]] = p

        combined_docs = list(old_docs_map.values())

        index_col.update_one(
            {"word": word},
            {"$set": {"docs": combined_docs}},
            upsert=True
        )

print("[Completed] TF-IDF calculation")
