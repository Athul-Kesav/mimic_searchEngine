import re
import nltk
from nltk.corpus import stopwords
from collections import defaultdict
from pymongo import MongoClient


# Setup
print("[Connecting] to DB")
client = MongoClient("mongodb://localhost:27017/")
db = client["search_engine"]
nltk.download('stopwords')
STOPWORDS = set(stopwords.words('english'))
index_col = db["inverted_index"]


def tokenize(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    tokens = text.split()
    tokens = [t for t in tokens if t not in STOPWORDS and len(t) > 2 and not t.isdigit()]
    return tokens


def search(query_tokens, inverted_index):
    scores = defaultdict(float)

    for token in query_tokens:
        if token in inverted_index:
            for doc in inverted_index[token]['docs']:
                scores[doc['link']] += doc['tfidf']

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return ranked

# Example usage
search_query = "Italy"

print("[Tokenizing] search query")
query_tokens = tokenize(search_query)

inverted_index = {}
for entry in index_col.find({}):
    inverted_index[entry['word']] = {"docs": entry.get("docs", [])}

print("-------------------------------Results----------------------------------")

results = search(query_tokens, inverted_index)

count = 0
for res in results:
    if count > 10:
        break
    print(res[0], f"|| score: {res[1]}")
    count += 1
