from elasticsearch import Elasticsearch, helpers
import json

es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

mapping = {
    "settings": {
        "index": {
            "number_of_shards": 1,
            "number_of_replicas": 1
        },
        "analysis": {
            "analyzer": {
                "sinhala_ngram_analyzer": {
                    "type": "custom",
                    "tokenizer": "icu_tokenizer",
                    "filter": [
                        "ngram_filter"
                    ]
                },
                "sinhala_analyzer_sw": {
                    "type": "custom",
                    "tokenizer": "icu_tokenizer",
                    "filter": [
                        "sinhala_stop"
                    ]
                },
                "english_ngram_analyzer": {
                    "type": "custom",
                    "tokenizer": "classic",
                    "filter": [
                        "ngram_filter"
                    ]
                }
            },
            "filter": {
                "ngram_filter": {
                    "type": "edge_ngram",
                    "min_gram": 2,
                    "max_gram": 20,
                    "side":"front"
                },
                "sinhala_stop": {
                    "type":"stop",
                    "stopwords":[]
                }
            }
        }
    },
    "mappings": {
        "properties": {
            "biography_en": {
                "type": "text"       
            },
            "biography_si": {
                "type": "text",
                "analyzer": "sinhala_analyzer_sw"
            },
            "birth_en": {
                "type": "text"
            },
            "birth_si": {
                "type": "text"
            },
            "death_en": {
                "type": "text"
            },
            "death_si": {
                "type": "text"
            },
            "filmography_en": {
                "properties": {
                    "film_name_en": {
                        "type": "text",
                        "analyzer": "english_ngram_analyzer"
                    },
                    "role_name_en": {
                        "type": "text",
                        "analyzer": "english_ngram_analyzer"
                    }
                }
            },
            "filmography_si": {
                "properties": {
                    "film_name_si": {
                        "type": "text",
                        "analyzer": "sinhala_ngram_analyzer"
                    },
                    "role_name_si": {
                        "type": "text",
                        "analyzer": "sinhala_ngram_analyzer"
                    }
                }
            },
            "known_as_en": {
                "type": "text",
                "analyzer": "english_ngram_analyzer"
            },
            "known_as_si": {
                "type": "text",
                "analyzer": "sinhala_ngram_analyzer"
            },
            "national_awards_en": {
                "properties": {
                    "award_ceremony_name_en": {
                        "type": "text",
                        "analyzer": "english_ngram_analyzer"
                    },
                    "award_name_en": {
                        "type": "text",
                        "analyzer": "english_ngram_analyzer"
                    },
                    "film_name_en": {
                        "type": "text",
                        "analyzer": "english_ngram_analyzer"
                    }
                }
            },
            "national_awards_si": {
                "properties": {
                    "award_ceremony_name_si": {
                        "type": "text",
                        "analyzer": "sinhala_ngram_analyzer"
                    },
                    "award_name_si": {
                        "type": "text",
                        "analyzer": "sinhala_ngram_analyzer"
                    },
                    "film_name_si": {
                        "type": "text",
                        "analyzer": "sinhala_ngram_analyzer"
                    }
                }
            },
            "real_name_en": {
                "type": "text",
                "analyzer": "english_ngram_analyzer"
            },
            "real_name_si": {
                "type": "text",
                "analyzer": "sinhala_ngram_analyzer"
            }
        }
    }
}


def json_bulk_upload():
    with open('../artists-corpus/sinhala_artists_data.json') as f:
        data = json.loads(f.read())

    # stopwords
    sw_temp = open("stop_words.txt",'r', encoding="utf8").read().split('\n')
    mapping["settings"]["analysis"]["filter"]["sinhala_stop"]["stopwords"] = sw_temp

    res1 = es.indices.create(index='index-artists', body=mapping)

    res2 = helpers.bulk(es, data, index='index-artists')

    print("Response:", res1)
    print("Response:", res2)


if __name__ == "__main__":
    json_bulk_upload()
