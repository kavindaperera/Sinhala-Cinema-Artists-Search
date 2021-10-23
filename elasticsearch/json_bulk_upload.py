from elasticsearch import Elasticsearch, helpers
import json

es = Elasticsearch([{'host': 'localhost', 'port':9200}])

def json_bulk_upload():
    with open('../artists-corpus/clean_artists_data.json') as f:
        data = json.loads(f.read())
        
    res = helpers.bulk(es, data, index='index-artists', doc_type='artist')

    print ("Response:", res)


if __name__ == "__main__":
    json_bulk_upload()