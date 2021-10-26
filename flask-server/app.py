import re
from flask import Flask, render_template, request
from flask_restful import Api, Resource
from elasticsearch import Elasticsearch, helpers, ElasticsearchException
import requests
import json
from sinling import SinhalaTokenizer, word_splitter

NODE_NAME = "index-artists"
TITLE = "සිංහල සිනමාවේ කලාකරුවන්"

es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

app = Flask(__name__)

tokenizer = SinhalaTokenizer()

acted_identifiers = ["රගපැ", "රගපාපු", "රඟපැ", "රඟපාපු"]
role_identifers = ["නළුවන්", "නිළියන්", "කලාකරුවන්"]
actor_identifers = ["නළුවන්", "නළුවා", "නළුව"]
actress_identifers = ["නිළියන්", "නිළිය", "නිලිය"]
film_identifiers = ["චිත්‍රපටයේ", "චිත්‍රපටය"]
award_identifiers = ["සම්මානය", "සම්මාන"]
award_ceremony_identifiers = ["සම්මාන", "සම්මානය", "උලෙල", "උළෙල"]
won_identifiers = ["දිනූ", "ජයග්‍රහනය",
                   "ජයග්‍රහණය", "ජයග්‍රහණය කල", "ජයග්‍රහණය කරපු"]
stop_words = open("stop_words.txt", 'r', encoding="utf8").read().split('\n')


class QueryProcessor:

    @classmethod
    def processingQuery(self, query):

        tokens = tokenizer.tokenize(query)
        must_list, should_list = self.classifyIntent(
            tokens=tokens, query=query)

        return must_list, should_list

    @classmethod
    def getAnalyzer(self,tokens):
        stortest_string = min(tokens, key=len)
        if(len(stortest_string)<3):
            return "sinhala_ngram_analyzer"
        else:
            return "sinhala_ngram_analyzer_2"   


    @classmethod
    def classifyIntent(self, tokens, query):

        must_list = []
        should_list = []

        for token in tokens:
            if(len(token) > 2):
                splits = word_splitter.split(token)
                # print(splits)

                if (splits['affix'] == "ේ") and (token not in film_identifiers):
                    should_list.append({
                        "match": {
                            "filmography_si.film_name_si": {
                                "query": token,
                                "analyzer": "sinhala_ngram_analyzer_2"
                            }
                        }
                    })

            if(token in acted_identifiers) or (token in film_identifiers):
                # print(token)
                idx = tokens.index(token) - 1
                if idx >= 0:
                    must_list.append({
                        "match": {
                            "filmography_si.film_name_si": {
                                "query": ' '.join(tokens[:idx+1]),
                                "analyzer": self.getAnalyzer(tokens)
                            }
                        }
                    })

            if(token in won_identifiers) or (token in award_ceremony_identifiers):
                idx = tokens.index(token) - 1
                if idx >= 0 and (token not in won_identifiers):
                    must_list.append({
                        "match": {
                            "national_awards_si.award_ceremony_name_si": ' '.join(tokens[:idx+1])
                        }
                    })

            if(token in actor_identifers):
                should_list.append({
                    "match": {
                        "filmography_si.role_name_si": "නළුවා"
                    }
                })

            if(token in actress_identifers):
                should_list.append({
                    "match": {
                        "filmography_si.role_name_si": "නිළිය"
                    }
                })

        return must_list, should_list


@app.route("/")
def home():
    artist_name = request.args.get("artist_name")

    artists_data = ""
    es_error = ""
    artist_list = []

    if artist_name:

        try:
            artists_data = es.search(index=NODE_NAME,
                                     query={
                                         "multi_match": {
                                             "query": "{}".format(artist_name),
                                             "fields": ["real_name_si", "known_as_si"]
                                         }
                                     }, size=100)

        except ElasticsearchException as e:
            es_error = e
            print(es_error)

        if artists_data:
            for artist in artists_data['hits']['hits']:
                artist_list.append(artist['_source'])

        return render_template("index.html", q="", search=artist_name,  artist_name=artist_name, about_artist=(artist_list[0] if len(artist_list) > 0 else ""), data=artist_list, es_error=es_error, title=TITLE)

    else:

        try:
            artists_data = es.search(index=NODE_NAME,
                                     body={"size": 500,
                                           "query": {
                                               "match_all": {}}
                                           }
                                     )

        except ElasticsearchException as e:
            es_error = e
            print(es_error)

        if artists_data:
            for artist in artists_data['hits']['hits']:
                artist_list.append(artist['_source'])

        return render_template("index.html", q="", search="", artist_name="", about_artist=(artist_list[0] if len(artist_list) > 0 else ""), data=artist_list, es_error=es_error, title=TITLE)


@app.route('/autocomplete', methods=["GET", "POST"])
def autocomplete():
    data = request.form.get("data")
    print("Suggest For:", data)

    res = es.search(index=NODE_NAME,
                    body={
                        "size": 10,
                        "query": {
                            "wildcard": {
                                "known_as_si.keyword": {
                                    "value": "{}*".format(data)
                                }
                            }
                        }
                    })

    return res


@ app.route('/search', methods=["GET", "POST"])
def search():
    q = request.args.get("q")

    preprocessor = QueryProcessor()

    must_list, should_list = preprocessor.processingQuery(query=q)

    artists_data = ""
    es_error = ""
    artist_list = []

    print("must_list: ", must_list)
    print("should_list: ", should_list)

    if len(must_list) > 0 or len(should_list) > 0:
        try:
            artists_data = es.search(index=NODE_NAME,
                                     body={
                                         "size": 100,
                                         "query": {
                                             "bool": {
                                                 "must": must_list,
                                                 "should": should_list
                                             }
                                         }
                                     })

        except ElasticsearchException as e:
            es_error = e
            print(es_error)

        if artists_data:
            for artist in artists_data['hits']['hits']:
                artist_list.append(artist['_source'])

        return render_template("index.html", q=q, search=q, artist_name="", about_artist=(artist_list[0] if len(artist_list) > 0 else ""), data=artist_list, es_error=es_error, title=TITLE)

    else:
        try:
            artists_data = es.search(index=NODE_NAME,
                                     body={
                                         "size": 100,
                                         "query": {
                                             "multi_match": {
                                                 "query": "{}".format(q),
                                                 "fields": ["real_name_si", "known_as_si",
                                                            "birth_si", "death_si",
                                                            "filmography_si.film_name_si",
                                                            "biography_si",
                                                            "national_awards_si.award_ceremony_name_si",
                                                            "national_awards_si.award_name_si",
                                                            "national_awards_si.film_name_si"],
                                                 "analyzer": "standard",
                                                 "zero_terms_query": "all"
                                             }
                                         }
                                     })

        except ElasticsearchException as e:
            es_error = e
            print(es_error)

        if artists_data:
            for artist in artists_data['hits']['hits']:
                artist_list.append(artist['_source'])

        return render_template("index.html", search=q, artist_name="", about_artist=(artist_list[0] if len(artist_list) > 0 else ""), data=artist_list, es_error=es_error, title=TITLE)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
