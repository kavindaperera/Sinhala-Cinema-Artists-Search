<!-- PROJECT LOGO -->
<br />
<div align="center">
  <h3 align="center">Sinhala-Cinema-Artists-Search</h3>
  <p align="center">
    Sinhala Cinema Actors and Actresses Search Engine created using Elasticsearch and Web Scraping!
    <br />
    <a href="https://github.com/">View Demo</a>
  </p>
</div>

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
    <li><a href="#techniques-used-in-designing-indexing-and-querying">Techniques Used in Designing Indexing and Querying</a></li>
    <li><a href="#advanced-features">Advanced Features</a></li>
    <li><a href="#getting-started">Getting Started</a></li>
    <li><a href="#repository-structure">Repository Structure</a></li>
  </ol>
</details>

## About The Project

## About Data

### No of Records

- The artist corpus contains data about more than 350 well-known actors and actresses. Data was be extracted from [website](films.lk)

### Data Fields



### Data Scraping



## Techniques Used in Designing Indexing and Querying



## Advanced Features



## Getting Started


###  Setup virtual environement
```
$ python3 -m venv venv
$ venv\Scripts\activate
$ pip install -r requirements.txt
```
### Elasticsearch
```
cd elasticsearch
python json_bulk_upload.py
```
### Start flask-server
```
cd flask-server
npm install
python app.py

```

## Repository Structure

    ├── artists-corpus : data scraped from (http://films.lk/)                    
        ├── artists_data.json : raw artist data
        ├── artists_link.csv : links to the artists single pages 
        └── clean_artists_data.json : translated artists data
    ├── elasticsearch : 
        └── json_bulk_upload.py :
    ├── examples : example queries     
    ├── flask-server : flask web app
        ├── static : frontend related files
        ├── templates : frontend related files
        └── index.py : backend related files 
    ├── requirements.txt : virtual environment requirements   
    ├── scraper.ipynb : jupyter notebook for web scaper 
    ├── translator.ipynb : jupyter notebook for translation and transliteration
       
