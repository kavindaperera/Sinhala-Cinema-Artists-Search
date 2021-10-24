import re
from flask import Flask, render_template, request
from flask_restful import Api, Resource
from elasticsearch import Elasticsearch, helpers, ElasticsearchException
import requests
import json
from sinling import SinhalaTokenizer, word_splitter

NODE_NAME = "index-artists"

es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

app = Flask(__name__)

tokenizer = SinhalaTokenizer()

acted_identifiers = ["යේ", "රගපැ", "රගපාපු", "රඟපැ", "රඟපාපු"]
role_identifers = ["නළුවන්", "නිළියන්"]
film_identifiers = ["චිත්‍රපටයේ", "චිත්‍රපටය"]


class QueryProcessor:

    @classmethod
    def processingQuery(self, query):

        tokens = tokenizer.tokenize(query)
        search_fields, query = self.classifyIntent(tokens=tokens, query=query)

        return search_fields, query

    @classmethod
    def classifyIntent(self, tokens, query):

        search_fields = []

        for token in tokens:

            splits = word_splitter.split(token)

            if(token in acted_identifiers or splits['affix'] == "යේ"):
                search_fields.append("filmography_si.film_name_si")
                query = query.replace(token, "")

            if(token in role_identifers):
                query = query.replace(token, "")

        return search_fields, query.strip()


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
                                     }, size=10)

        except ElasticsearchException as e:
            es_error = e
            print(es_error)

        if artists_data:
            for artist in artists_data['hits']['hits']:
                artist_list.append(artist['_source'])

        return render_template("index.html", search="", artist_name=artist_name, data=artist_list, es_error=es_error, title="සිංහල කලාකරුවන්")

    else:

        try:
            artists_data = es.search(index=NODE_NAME,
                                     query={
                                         "match_all": {}
                                     }, size=10)

        except ElasticsearchException as e:
            es_error = e
            print(es_error)

        if artists_data:
            for artist in artists_data['hits']['hits']:
                artist_list.append(artist['_source'])

        return render_template("index.html", search="", data=artist_list, es_error=es_error, title="සිංහල කලාකරුවන්")


@app.route('/autocomplete', methods=["GET", "POST"])
def autocomplete():
    data = request.form.get("data")
    print("Suggest For:", data)

    res = es.search(index=NODE_NAME,
                    query={
                        "wildcard": {
                            "known_as_si.keyword": {
                                "value": "{}*".format(data)
                            }
                        }})

    return res


@app.route('/search', methods=["GET", "POST"])
def search():
    q = request.args.get("q")

    preprocessor = QueryProcessor()

    search_fields, query = preprocessor.processingQuery(query=q)

    artists_data = ""
    es_error = ""
    artist_list = []

    print("Search For:", query, " in ", search_fields)

    if len(search_fields) > 0:
        try:
            artists_data = es.search(index=NODE_NAME,
                                     query={
                                         "multi_match": {
                                             "query": "{}".format(query),
                                             "fields": search_fields
                                         }
                                     }, size=10)

        except ElasticsearchException as e:
            es_error = e
            print(es_error)

        if artists_data:
            for artist in artists_data['hits']['hits']:
                artist_list.append(artist['_source'])

        return render_template("index.html", search=q, artist_name="", data=artist_list, es_error=es_error, title="සිංහල කලාකරුවන්")

    else:
        try:
            artists_data = es.search(index=NODE_NAME,
                                     query={
                                         "multi_match": {
                                             "query": "{}".format(query),
                                             "fields": ["filmography_si.film_name_si",
                                                        "biography_si",
                                                        "national_awards_si.award_ceremony_name_si",
                                                        "national_awards_si.award_name_si",
                                                        "national_awards_si.film_name_si"],
                                             "analyzer": "sinhala_analyzer_sw"
                                         }
                                     }, size=10)

        except ElasticsearchException as e:
            es_error = e
            print(es_error)

        if artists_data:
            for artist in artists_data['hits']['hits']:
                artist_list.append(artist['_source'])

        return render_template("index.html", search=q, artist_name="", data=artist_list, es_error=es_error, title="සිංහල කලාකරුවන්")


if __name__ == "__main__":
    app.run(debug=True, port=5000)
