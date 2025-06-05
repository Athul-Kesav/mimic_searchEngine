import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pymongo import MongoClient

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["search_engine"]
collection = db["pages"]

# href Finder
def htmlParserToGetHrefs(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')
    anchors = soup.find_all('a', href=True)
    absolute_links = []

    for a in anchors:
        href = a['href']
        full_url = urljoin(base_url, href) 
        if full_url.startswith("http"):
            absolute_links.append(full_url)
    
    return absolute_links

# Init
seed = "https://bangalore.craigslist.org/" # also https://www.bbc.com/
queue = [seed]
visited = set()
inout_map = dict()  # {link: [in, out]} to find inbound and outgoing links
MAX_LINKS = 500 # upto 500 links crawled

# Crawler
while queue and len(visited) < MAX_LINKS:
    url = queue.pop(0)
    if url in visited:
        continue
    
    try:
        res = requests.get(url, timeout=5) # [GET] url
        visited.add(url) # add to visited
    except:
        continue

    html = res.text
    outlinks = htmlParserToGetHrefs(html, url) # get all outlinks

    # Add new outlinks to queue
    for link in outlinks:
        if link not in visited and link not in queue:
            queue.append(link)
        
        # Update in-count
        if link not in inout_map:
            inout_map[link] = [0, 0]
        inout_map[link][0] += 1     # increment in

    # Update out count for current URL
    if url not in inout_map:
        inout_map[url] = [0, 0]
    
    inout_map[url][1] = len(outlinks)

    print(f"[{len(visited)}] Visited: {url}, outlinks: {len(outlinks)}")

# Save to MongoDB
for link, (in_count, out_count) in inout_map.items():
    weight = in_count / out_count if out_count != 0 else 0
    collection.update_one(
        {"link": link},
        {"$set": {"in": in_count, "out": out_count, "weight": weight}},
        upsert=True
    )

print("[Completed] Crawling and DB update")
