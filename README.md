<!-- PROJECT LOGO -->
<br />
<div align="center">
  <h3 align="center">Sinhala-Cinema-Artists-Search</h3>
  <p align="center">
    Sinhala Cinema Actors and Actresses Search Engine created using Elasticsearch and Web Scraping!
    <br />
    <a href="https://github.com/kavindaperera/Sinhala-Cinema-Artists-Search/">View Repository</a>
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
        <li><a href="#data-scraping-and-cleaning">Data Scraping and Cleaning</a></li>
      </ul>
    </li>
    <li><a href="#techniques-used-in-designing-indexing-and-querying">Techniques Used in Designing Indexing and Querying</a></li>
    <li><a href="#advanced-features">Advanced Features</a></li>
    <li><a href="#getting-started">Getting Started</a></li>
    <li><a href="#repository-structure">Repository Structure</a></li>
  </ol>
</details>

## About The Project

The main objective of the project is to develop a search engine for well-known Sinhala cinema actors and actresses. Search engine supports Sinhala language. Users can search using different types of Sinhala Language queries. Elasticsearch is used for designing indexing and querying and flask is used as the back-end. 

![ Main](/images/main.gif?raw=true "Main ")

## About Data

### No of Records

- The artist corpus contains data about more than 350 well-known actors and actresses. Data was extracted from [films.lk](https://www.films.lk). 

### Data Fields

Each artist contains following data fields in both Sinhala and English. `_si` and `_en` tags are used to identify the language.

* `know_as` : Artists well known name in the cinema industry
* `real_name` : Real born name of the artist
* `birth` : Date of Birth
* `death` : Date of Death
* `biography` : A short biogrpahy about the artist
* `national_awards` : National level awards won by the artist
  * `award_ceremony_name` : Award Ceremony name
  * `award_name` : Awarded category
  * `film_name` : Awarded film
* `filmography` : Filmography of the artist as a cast member
  * `film_name` : Name of the film
  * `role_name` : Role played [`Main Actor`, `Main Actress`, `Actor`,`Actress`]

### Data Scraping and Cleaning

- All the data is scraped from [films.lk](https://www.films.lk). 
- [Beautiful Soup](https://pypi.org/project/beautifulsoup4/) which is Python library for pulling data out of HTML and XML files
is used for scraping the website. 
- First the required data is extracted in english language and was stored in `json` format. `scraper.ipynb` notebook contains this process. 
- Then those data is translated to sinhala language using google translate api. Some of the fields like names and film names are transliterated. `translator.ipynb` notebook contains this process. 
- Finally the translated data is cleaned and some major translation mistakes are fixed. `data-cleaning.ipynb` notebook contains this process.
- All the `json` formatted data are included in the `artist-corpus` folder and `clean_artists_data.json` contains the final data.


## Techniques Used in Designing Indexing and Querying

For indexing and querying the Elasticsearch is used. Some of the bult-in tokenziers and new custom stopword filters were used as follows.

1. Tokenizing
  - ICU_tokenizer 
    - This Tokenizes text into words on word boundaries, as defined in [UAX #29: Unicode Text Segmentation](https://www.unicode.org/reports/tr29/). It behaves much like the `standard tokenizer`, but adds better support for some Asian language like Sinhala. This is used on all sinhala language text fields at index time.
  - Standard Tokenizer 
    - The `standard tokenizer` provides grammar based tokenization.This tokenizer is also used during some of the query tokenizing. 
2. Stopwords Filter
  - Sinhala Stop words filter 
    - Elastic search does not support `sinhala` stop work filtering. A custom sinhala stop was filter is created for sinhala language. This filter was used on `biography_si` field.
    - The list of stop words can be found in [stopwords.txt](/elasticsearch/stop_words.txt) 

3. Edge n-gram token filter
  - The `edge_ngram` filter is similar to a `n_gram` token flter. But, it ponly outputs n-grams that start at the begining of the token.
  - This n-gram filter is used on all the fields except `biography`, `birth` and `death`. Different configuration were used according to the nature of the field. 
  - For example the name  `රුක්මනී දේවි` produce the terms `["රු", "රුක", "රුක්", "රුක්ම", "රුක්මන", "රුක්මනී", "දේ", "දේව", "දේවි"]`.
  - This filter helps to identify spelling mistakes and to do wildcard queries on sinhala text. Further explained the `Advanced Features` section.

The [mapping.json](/elasticsearch/mapping.json) file shows how each of these techniques where used on different fields in elasticsearch. Following `json` shows how different `analyzers` and `filters` were created using above mentioned techniques:

<details>
  <summary>Click to Expand!</summary>
  
  ```javascript
{
  "index-artists": {
    "settings": {
      "index": {
        "routing": {
          "allocation": {
            "include": {
              "_tier_preference": "data_content"
            }
          }
        },
        "number_of_shards": "1",
        "provided_name": "index-artists",
        "creation_date": "1635233423927",
        "analysis": {
          "filter": {
            "ngram_filter_2": {
              "min_gram": "4",
              "side": "front",
              "type": "edge_ngram",
              "max_gram": "20"
            },
            "ngram_filter_1": {
              "min_gram": "1",
              "side": "front",
              "type": "edge_ngram",
              "max_gram": "20"
            },
            "sinhala_stop": {
              "type": "stop",
              "stopwords": [stop_words.txt]
            },
            "ngram_filter": {
              "min_gram": "2",
              "side": "front",
              "type": "edge_ngram",
              "max_gram": "20"
            }
          },
          "analyzer": {
            "english_ngram_analyzer": {
              "filter": [
                "ngram_filter"
              ],
              "type": "custom",
              "tokenizer": "classic"
            },
            "sinhala_ngram_analyzer_1": {
              "filter": [
                "ngram_filter_1"
              ],
              "type": "custom",
              "tokenizer": "icu_tokenizer"
            },
            "sinhala_ngram_analyzer_2": {
              "filter": [
                "ngram_filter_2"
              ],
              "type": "custom",
              "tokenizer": "icu_tokenizer"
            },
            "english_ngram_analyzer_2": {
              "filter": [
                "ngram_filter_2"
              ],
              "type": "custom",
              "tokenizer": "classic"
            },
            "sinhala_analyzer_sw": {
              "filter": [
                "sinhala_stop"
              ],
              "type": "custom",
              "tokenizer": "icu_tokenizer"
            },
            "english_ngram_analyzer_1": {
              "filter": [
                "ngram_filter_1"
              ],
              "type": "custom",
              "tokenizer": "classic"
            },
            "sinhala_ngram_analyzer": {
              "filter": [
                "ngram_filter"
              ],
              "type": "custom",
              "tokenizer": "icu_tokenizer"
            }
          }
        },
        "number_of_replicas": "1",
        "uuid": "5J2kRxWLTT-8nOmDywHE0A",
        "version": {
          "created": "7150199"
        }
      }
    }
  }
}
  ```
</details>




## Advanced Features

1.	Completion Suggestions
  - Search engine supports autocomplete for artists names. This was achieved using wildcard queries and Edge N-gram Token Filter. It will suggest artist names as you type on the search box. Following diagram shows how suggestions work: 

![Autocomplete Suggestions](/images/autocomplete.jpg?raw=true "Autocomplete Suggestions")

2. Search will work for misspelled words
  - With the help of Edge N-gram Tokenizer, the queries will tolerate typos. 
  - For example, `අයිරාගනී` or `අයිරාගනී රණසිංහ` will return correct results for `අයිරාංගනී සේරසිංහ` and `මහින්දාගම චිත්‍රපටයේ නළුවන්` will return same results as in `මහින්දාගමනය චිත්‍රපටයේ නළුවන්`.

3.	Faceting and Rule based query intent classification
  - Query is passed to a intent classifier before passing the request to elasticsearch. 3 types of intents were first identified and queries are classified according to them. For this, queries are first tokenized using a sinhala language tokenizer `sinling`. After that, TF-IDF vectorization and cosine similarity are used for classification. This  enables the search engine to support additional queries like:
  ```
  මහින්දාගමනය චිත්‍රපටය
  මහින්දාගමනය චිත්‍රපටයේ නළුවන්
  මහින්දාගමනය චිත්‍රපටයේ රඟපැ නළුවන්
  මහින්දාගමනයේ නළුවන්
  මහින්දාගමනය චිත්‍රපටයේ රඟපැ නිළියන්
  මහින්දාගමනයේ නිළියන්
  කඩවුණු පොරොන්දුව චිත්‍රපටයේ නළුවන්
  කඩවුණු පොරොන්දුව චිත්‍රපටයේ නිළියන්
  
  සරසවිය සම්මාන
  සරසවිය සම්මාන දිනූ නළුවන්
  සරසවිය සම්මාන දිනූ නිළියන්
  ජනාධිපති සම්මානය දිනූ නළුවන්
  ජනාධිපති සම්මානය දිනූ නිළියන්
  සරසවිය සම්මාන ජයග්‍රහණය කල නළුවන්
  සරසවිය සම්මාන ජයග්‍රහණය කල නිළියන්
  14 වන සරසවිය සම්මානය දිනූ නළුවා
  ```
  - `bool` query feature of elasticsearch is also used for this purpose. The query tokens will be classified as `must` and `should` which will help to rank and boost the results. 
    - For example a query with term `නළුවන්` should return all the actors followed by actresses. Similarly, a query with term `නිළියන්` should return all the actresses followed by actors. Including the term `නළුවා` or `නිළිය` on `should` will boost the results accordingly. 
    - A query like `මහින්දාගමනය චිත්‍රපටයේ රඟපැ නළුවන්` or `කඩවුණු පොරොන්දුව චිත්‍රපටයේ නළුවන්` will classify the query tokens and include `මහින්දාගමනය` or `කඩවුණු පොරොන්දුව` as a `must` in `film_name_si` field and `නළුවා` or `නිළිය` as `should` in `role_name_si` field. This will return all the actors followed by actresses or actresses followed by actors who were in the cast of those films.


## Getting Started


###  Setup virtual environement

Complete the following steps to setup a virtual environment and install all the required libraries:

```
$ python3 -m venv venv
$ venv\Scripts\activate
$ pip install -r requirements.txt
```

### Elasticsearch
You need to first setup elasticsearch locally. Once elasticsearch is ready, start elasticsearch on port `localhost:9200`.
Run the following command to setup `icu_tokenizer` plugin on your elsaticsearch cluster:

```
sudo bin/elasticsearch-plugin install analysis-icu
```

Then run the following commands to index `index-artists` on your local elasticsearch cluster:

```
cd elasticsearch
python json_bulk_upload.py
```

You can check whether the indexing was successful by sending a `GET` reqeust to `localhost:9200/index-artists/` , which will return in the index mapping.

### Start Flask Application
Once the elasticsearch is up and running, run the following commands to start the `flask` application:

```
cd flask-server
python app.py
```
Now you can open the browser and search engine will run on `127.0.0.1:5000/`.

## Repository Structure

    ├── artists-corpus : data scraped from (http://films.lk/)                    
        ├── artists_data.json : raw artist data
        ├── artists_link.csv : links to the artists single pages 
        ├── sinhala_artists_data.json : translated artist data
        └── clean_sinhala_artists_data.json : final cleaned artists data
    ├── elasticsearch : 
        ├── mapping.json : index mapping for elasticsearch
        ├── json_bulk_upload.py : elasticsearch bulk insert
        └── stop_words.txt : sinhala stopwords list
    ├── examples : example queries     
    ├── flask-server : flask web app
        ├── static : frontend related files
        ├── templates : frontend related files
        ├── app.py : backend related files 
        └── stop_words.txt : sinhala stopwords list
    ├── data-cleaning.ipynb : jupyter notebook for data cleaning 
    ├── requirements.txt : virtual environment requirements   
    ├── scraper.ipynb : jupyter notebook for web scaper 
    ├── translator.ipynb : jupyter notebook for translation and transliteration
    

       
