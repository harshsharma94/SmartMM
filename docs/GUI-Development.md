Possible options available for Development with Python
------------------------------------------------------
server requirement ?

* PyQt
will be suitable for now. After finishing all the research work, we can later on extend the tool to other frameworks.
* Django App
steep learning curve. will require mvc framework.
* Flask
Probably all decent browsers prevent arbitrary filesystem access.
You can however use javascript to select all files in a directory and 
iterate over them creating an upload field in your multipart form for each one of them.
Options after Research.
* Node.js(AppJS)
* Chrome App with Web View ?
* Supporter Desktop app with a Django server

Scraping ? Any other database ?

Proposed Methods

| Keyword Extraction Methods        | Pros         | Cons  |
| ------------- |:-------------:| -----:|
| Co-occurence (RAKE)(2010) |  Statistical, Very good results comparitively, Domain applicable, can also be used for individual documents. No corpus required. Easy to implement| Less Linguistic knowledge used |
| TFIDF      |   Applicable for Multiple Documents, Easy to implement.  | Requires a corpus, lacks Parts of Speech and Adjacent frequency |
| POS Unsupervised |   TFIDF + POS filtering , Use of graph improves results  | Supervised has better results, Clustering in Movie Domain is questionable |
|Supervised|---|Requires labeled training data, which is not available for Movie Reviews
|Graph Based|TextRank: Works on reccomendation/relation between words/sentences and syntactic filters with co-occurence, Most used by Citations. Linguistic information helps keyword extraction.| Domain-specific


Further Additions:
-----------------
* wikipedia movie categories at the end: Keywords - clean
* production cost and other attributes from wikipedia
* Subtitles: Keyword Extraction
* Twitter sentiment analysis
