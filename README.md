# Sinhala-Cinema-Artists-Search
Sinhala Cinema Actors and Actresses Search Engine created using Elasticsearch and Web Scraping

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
    </li>
    <li>
      <a href="#about-data">About Data</a>
      <ul>
        <li><a href="#no-of-records">No of Records</a></li>
        <li><a href="#data-fields">Data Fields</a></li>
        <li><a href="#data-scraping">Data Scraping</a></li>
      </ul>
    </li>
    <li><a href="#techiques-used-in-designing-indexing-and-querying">Techniques Used in Designing Indexing and Querying</a></li>
    <li><a href="#advanced-features">Advanced Features</a></li>
    <li><a href="#getting-started">Getting Started</a></li>
    <li><a href="#repository-structure">Repository Structure</a></li>
  </ol>
</details>

## About The Project

## About Data

### No of Records

The artist corpus contains data about more than 350 well-known actors and actresses. Data was be extracted from [website](films.lk)

### Data Fields



### Data Scraping



## Techniques Used in Designing Indexing and Querying



## Advanced Features



## Getting Started



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
       
