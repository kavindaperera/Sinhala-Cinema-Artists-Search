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

- The artist corpus contains data about more than 350 well-known actors and actresses. Data was extracted from [films.lk](films.lk)

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

- All the data is scraped from [films.lk](films.lk). 
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
    - This is the recommended tokenizer by elastic search for unicode.  ICU tokenizer is used on all sinhala language data fields when indexing.
  - Standard Tokenizer 
    - Standard tokenizer is used during some of the query tokenizing.  
2. Stopwords Filter
  - Sinhala Stop words filter 
    - Elastic search only supports english stopwords filter. A custom sinhala stop was filter is created for sinhala language. This filter was on `biography` field. 

3. Edge n-gram tokenizer
  - This filter helps to identify spelling mistakes and to do wildcard queries on sinhala text. Further explained the `Advanced Features` section.
  - This n-gram filter is used on all the fields except `biography`, `birth` and `death`. Different configuration were used accoriding to the nature of the field. 
  - For example the name  `රුක්මනී දේවි` produce the terms `["රු", "රුක", "රුක්", "රුක්ම", "රුක්මන", "රුක්මනී", "දේ", "දේව", "දේවි"] `.

Following Elasticsearch mapping shows how each of these techniques where used on different fields:
```
{
  "index-artists" : {
    "mappings" : {
      "properties" : {
        "biography_en" : {
          "type" : "text"
        },
        "biography_si" : {
          "type" : "text",
          "analyzer" : "sinhala_analyzer_sw"
        },
        "birth_en" : {
          "type" : "text"
        },
        "birth_si" : {
          "type" : "text"
        },
        "death_en" : {
          "type" : "text"
        },
        "death_si" : {
          "type" : "text"
        },
        "filmography_en" : {
          "properties" : {
            "film_name_en" : {
              "type" : "text",
              "fields" : {
                "keyword" : {
                  "type" : "keyword",
                  "ignore_above" : 256
                }
              },
              "analyzer" : "english_ngram_analyzer"
            },
            "role_name_en" : {
              "type" : "text",
              "fields" : {
                "keyword" : {
                  "type" : "keyword",
                  "ignore_above" : 256
                }
              },
              "analyzer" : "english_ngram_analyzer"
            }
          }
        },
        "filmography_si" : {
          "properties" : {
            "film_name_si" : {
              "type" : "text",
              "fields" : {
                "keyword" : {
                  "type" : "keyword",
                  "ignore_above" : 256
                }
              },
              "analyzer" : "sinhala_ngram_analyzer"
            },
            "role_name_si" : {
              "type" : "text",
              "fields" : {
                "keyword" : {
                  "type" : "keyword",
                  "ignore_above" : 256
                }
              },
              "analyzer" : "sinhala_ngram_analyzer"
            }
          }
        },
        "known_as_en" : {
          "type" : "text",
          "fields" : {
            "keyword" : {
              "type" : "keyword",
              "ignore_above" : 256
            }
          },
          "analyzer" : "english_ngram_analyzer"
        },
        "known_as_si" : {
          "type" : "text",
          "fields" : {
            "keyword" : {
              "type" : "keyword",
              "ignore_above" : 256
            }
          },
          "analyzer" : "sinhala_ngram_analyzer"
        },
        "national_awards_en" : {
          "properties" : {
            "award_ceremony_name_en" : {
              "type" : "text",
              "fields" : {
                "keyword" : {
                  "type" : "keyword",
                  "ignore_above" : 256
                }
              },
              "analyzer" : "english_ngram_analyzer_2"
            },
            "award_name_en" : {
              "type" : "text",
              "fields" : {
                "keyword" : {
                  "type" : "keyword",
                  "ignore_above" : 256
                }
              },
              "analyzer" : "english_ngram_analyzer"
            },
            "film_name_en" : {
              "type" : "text",
              "fields" : {
                "keyword" : {
                  "type" : "keyword",
                  "ignore_above" : 256
                }
              },
              "analyzer" : "english_ngram_analyzer"
            }
          }
        },
        "national_awards_si" : {
          "properties" : {
            "award_ceremony_name_si" : {
              "type" : "text",
              "fields" : {
                "keyword" : {
                  "type" : "keyword",
                  "ignore_above" : 256
                }
              },
              "analyzer" : "sinhala_ngram_analyzer_2"
            },
            "award_name_si" : {
              "type" : "text",
              "fields" : {
                "keyword" : {
                  "type" : "keyword",
                  "ignore_above" : 256
                }
              },
              "analyzer" : "sinhala_ngram_analyzer"
            },
            "film_name_si" : {
              "type" : "text",
              "fields" : {
                "keyword" : {
                  "type" : "keyword",
                  "ignore_above" : 256
                }
              },
              "analyzer" : "sinhala_ngram_analyzer"
            }
          }
        },
        "real_name_en" : {
          "type" : "text",
          "fields" : {
            "keyword" : {
              "type" : "keyword",
              "ignore_above" : 256
            }
          },
          "analyzer" : "english_ngram_analyzer"
        },
        "real_name_si" : {
          "type" : "text",
          "fields" : {
            "keyword" : {
              "type" : "keyword",
              "ignore_above" : 256
            }
          },
          "analyzer" : "sinhala_ngram_analyzer"
        }
      }
    }
  }
}
```


## Advanced Features

1.	Completion Suggestions
  - Search engine supports autocomplete for artists names. This was achieved using wildcard queries and Edge N-gram Token Filter. It will suggest artist names as you type on the search box. Following diagram shows how suggestions work: 

![Autocomplete Suggestions](/images/autocomplete.jpg?raw=true "Autocomplete Suggestions")

2.	Faceting and Rule based query classification
  - Simple rule based classificationa are done before passing the request to elastic search. Few intents were first identified and queries are classified acoriding to them. For this, queries are first tokenized using a sinhala language tokenizer `siling`. This feature enables the search engine to support queries like:
  ```
  මහින්දාගමනය චිත්‍රපටයේ නළුවන්
  මහින්දාගමනය චිත්‍රපටයේ රඟපැ නළුවන්
  මහින්දාගමනයේ නළුවන්
  මහින්දාගමනය චිත්‍රපටයේ රඟපැ නිළියන්
  මහින්දාගමනයේ නිළියන්
  කඩවුණු පොරොන්දුව චිත්‍රපටයේ නළුවන්
  කඩවුණු පොරොන්දුව චිත්‍රපටයේ නිළියන්
  සරසවිය සම්මාන දිනූ නළුවන්
  සරසවිය සම්මාන දිනූ නිළියන්
  ජනාධිපති සම්මානය දිනූ නළුවන්
  ජනාධිපති සම්මානය දිනූ නිළියන්
  සරසවිය සම්මාන ජයග්‍රහණය කල නළුවන්
  සරසවිය සම්මාන ජයග්‍රහණය කල නිළියන්
  14 වන සරසවිය සම්මානය දිනූ නළුවා
  ```
  - `bool` query feature of elastic search was also used for this purpose. The query terms will be classified as `must` and `should` which will help to rank the results. For example a query with term `නළුවන්` will return all the actors followed by actresses. similarly, a query with term `නිළියන්` will return all the actresses followed by actors. 



## Getting Started


###  Setup virtual environement

Complete the following steps to create a virtual environment and install all the requirements.

```
$ python3 -m venv venv
$ venv\Scripts\activate
$ pip install -r requirements.txt
```

### Elasticsearch
You need to first setup elasticsearch locally. Once elasticsearch is ready, start elastic search on port `localhost:9200`
Do the following steps to index `index-artists` on your local elasticsearch cluster

```
cd elasticsearch
python json_bulk_upload.py
```

You can check whether the indexing was successful by sending a `GET` reqeust to `http://localhost:9200/index-artists/` , which will return in the index mapping.

### Start Flask Application
Once the elasticsearch is up and running, do the following steps to start the `flask` application.

```
cd flask-server
python app.py
```

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
    

       
