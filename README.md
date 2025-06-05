# 🔍 Mini Search Engine Pipeline

A basic end-to-end search engine pipeline built from scratch using Python. This project explores how search engines work internally—starting with crawling, then indexing, searching, and finally presenting results via a custom browser interface built using React Native.

---

## 🚧 Project Structure

1. **Crawler**  
   Crawls web pages, follows links, and gets raw HTML content for outgoing links. (Did not consider robots.txt, will implement that soon)

2. **Indexer**  
   Fetches fresh HTML content, tokenizes, and builds an inverted index using TF-IDF.

3. **Searcher**  
   Retrieves relevant documents from the index based on user queries.

4. **Browser Interface (React Native)**  
   Wraps the functionality in a mobile-friendly UI for searching and viewing results. (To be added)

---

## 🛠️ Tech Stack

- **Language**: Python (backend logic)
- **Frontend**: React Native
- **Database**: Local MongoDB (to store crawled pages, indexes, and search metadata)

---

## 📚 References & Inspiration

- [Build a Search Engine | YouTube - Kyle Bragger](https://youtu.be/HXBIr719tZg?si=kd_kiD8tVaFFUjoM)
- [Build Your Own X (Codecrafters)](https://github.com/codecrafters-io/build-your-own-x)
- [TF-IDF Explained by Steven Loria](https://stevenloria.com/tf-idf/)

---

## 🧠 Concepts Implemented

- Basic crawling and link-following (Crawled 16166 links using seeds - <www.bbc.com> and <www.nytimes.com>)
- HTML parsing and text extraction
- Inverted index construction (Indexed 59907 words using 5000 of the crawled links - system limitations)
- TF-IDF-based ranking
- Query parsing and search scoring (Scored using TF-IDF)
- React Native UI for search interaction (To Be Added)

---

## 🧪 Status

- 🚧 Work in progress.
Currently learning React-Native for the browser interface.

- PRs and suggestions are welcome.
