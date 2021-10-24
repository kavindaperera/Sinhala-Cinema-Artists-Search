from flask import Flask, render_template, request
from elasticsearch import Elasticsearch, helpers, ElasticsearchException
import requests

es = Elasticsearch([{'host': 'localhost', 'port':9200}])

app = Flask(__name__)

@app.route("/")
def home():

    artists_data = ""
    es_error = ""

    try:
        artists_data = es.search(index="index-artists", query={"match_all":{}})

    except ElasticsearchException as e:
        es_error = e
        print(es_error)   

    artist_list = []

    if artists_data:
        for artist in artists_data['hits']['hits']:
            artist_list.append(artist['_source'])    

    return render_template("index.html", data=artist_list, es_error=es_error, title="Sinhala Artist Search")



if __name__ == "__main__":
    app.run(debug=True)