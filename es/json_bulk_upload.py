from elasticsearch import Elasticsearch, helpers
import json

es = Elasticsearch([{'host': 'localhost', 'port':9200}])

def json_bulk_upload():
    with open('../artists-corpus/trans_artists_data.json') as f:
        data = json.loads(f.read())
        
    helpers.bulk(es, data, index='index-test', doc_type='test')


if __name__ == "__main__":
    json_bulk_upload()