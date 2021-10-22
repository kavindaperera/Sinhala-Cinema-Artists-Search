# Sinhala-Cinema-Artists-Search
Sinhala Cinema Actors and Actresses Search Engine created using Elasticsearch and Web Scraping

## Repository Structure

    ├── artists-corpus : data scraped from (http://films.lk/)                    
        ├── artists_data.json : raw artist data
        ├── artists_link.csv : links to the artists single pages 
        └── trans_artists_data.json : translated artists data
    ├── elasticsearch : 
        ├── json_bulk_upload.py :
        └── requirements.txt :
    ├── examples : example queries     
    ├── flask-server : flask web app
        ├── static : Frontend
        ├── templates : Frontend
        ├── index.py : Backend 
        └── requirements.txt :
    ├── scraper.ipynb : jupyter notebook for web scaper 
    ├── translator.ipynb : jupyter notebook for translation and transliteration
       
