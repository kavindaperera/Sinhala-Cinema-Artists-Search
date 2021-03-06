import re
from flask import Flask, render_template, request
from elasticsearch import Elasticsearch, helpers, ElasticsearchException
from sinling import SinhalaTokenizer, word_splitter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

NODE_NAME = "index-artists"
TITLE = "සිංහල සිනමාවේ කලාකරුවන්"

es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

app = Flask(__name__)

tokenizer = SinhalaTokenizer()

acted_identifiers = ["රගපැ", "රගපාපු", "රඟපැ", "රඟපාපු"]
role_identifers = ["නළුවා", "නිළිය"]
actor_identifers = ["නළුවන්", "නළුවා", "නළුව"]
actress_identifers = ["නිළියන්", "නිළිය", "නිලිය"]
film_identifiers = ["චිත්‍රපටයේ", "චිත්‍රපටය"]
award_identifiers = ["සම්මානය", "සම්මාන"]
award_ceremony_identifiers = ["සම්මාන", "සම්මානය", "උලෙල", "උළෙල"]
won_identifiers = ["දිනූ", "ජයග්‍රහනය",
                   "ජයග්‍රහණය", "ජයග්‍රහණය කල", "ජයග්‍රහණය කරපු"]
                   
stop_word_list = open("stop_words.txt", 'r', encoding="utf8").read().split('\n')


class QueryProcessor:

    @classmethod
    def processingQuery(self, query):

        tokens = tokenizer.tokenize(query)
        must_list, should_list = self.classifyIntent(
            tokens=tokens)

        return must_list, should_list

    @classmethod
    def getAnalyzer(self, tokens):
        shortest_string = min(tokens, key=len)
        if(len(shortest_string) < 3):
            return "sinhala_ngram_analyzer"
        else:
            return "sinhala_ngram_analyzer_2"

    @classmethod
    def getSimilarity(self, corpus):
        vectorizer = TfidfVectorizer(
            analyzer="char", token_pattern=u'(?u)\\b\w+\\b')
        X = vectorizer.fit_transform(corpus)
        cs = cosine_similarity(X[0:1], X)
        score_list = cs[0][1:]
        return score_list

    @classmethod
    def classifyIntent(self, tokens):

        intent_type = -1
        must_list = []
        should_list = []

        for token in tokens:
            corpus = [token]
            corpus.extend(acted_identifiers)
            corpus.extend(film_identifiers)
            max_score = max(self.getSimilarity(corpus))

            if max_score > 0.8:
                intent_type = 1  # movies

        if intent_type == 1:
            for token in tokens:
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

            query_words = [token for token in tokens if token not in acted_identifiers +
                           film_identifiers+actress_identifers+actor_identifers]
            query = ' '.join(query_words)

            must_list.append({
                "match": {
                    "filmography_si.film_name_si": {
                        "query": query,
                        "analyzer": self.getAnalyzer(query_words)
                    }
                }
            })

            return must_list, should_list

        for token in tokens:
            corpus = [token]
            corpus.extend(award_ceremony_identifiers)
            corpus.extend(won_identifiers)
            max_score = max(self.getSimilarity(corpus))

            if max_score > 0.8:
                intent_type = 2  # awards

        if intent_type == 2:
            for token in tokens:
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

            query_words = [token for token in tokens if token not in award_ceremony_identifiers +
                           won_identifiers+actress_identifers+actor_identifers]
            query = ' '.join(query_words)

            must_list.append({
                "match": {
                    "national_awards_si.award_ceremony_name_si": query
                }
            })

            return must_list, should_list

        for token in tokens:
            corpus = [token]
            corpus.extend(actor_identifers)
            corpus.extend(actress_identifers)
            max_score = max(self.getSimilarity(corpus))

            if max_score > 0.8:
                intent_type = 3  # gender only

        if intent_type == 3:
            for token in tokens:
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

            query_words = [
                token for token in tokens if token not in actress_identifers+actor_identifers]
            query = ' '.join(query_words)

            must_list.append({
                "multi_match": {
                    "query": query,
                    "fields": ["real_name_si", "known_as_si",
                               "birth_si", "death_si",
                               "filmography_si.film_name_si",
                               "biography_si",
                               "national_awards_si.award_ceremony_name_si",
                               "national_awards_si.award_name_si",
                               "national_awards_si.film_name_si"],
                    "analyzer": self.getAnalyzer(query_words),           
                }
            })

            return must_list, should_list

        return must_list, should_list

        # for token in tokens:
        #     if(token in acted_identifiers) or (token in film_identifiers):
        #         idx = tokens.index(token) - 1
        #         if idx >= 0:
        #             must_list.append({
        #                 "match": {
        #                     "filmography_si.film_name_si": {
        #                         "query": ' '.join(tokens[:idx+1]),
        #                         "analyzer": self.getAnalyzer(tokens)
        #                     }
        #                 }
        #             })

        #     if(token in won_identifiers) or (token in award_ceremony_identifiers):
        #         idx = tokens.index(token) - 1
        #         if idx >= 0 and (token not in won_identifiers):
        #             must_list.append({
        #                 "match": {
        #                     "national_awards_si.award_ceremony_name_si": ' '.join(tokens[:idx+1])
        #                 }
        #             })

        #     if(token in actor_identifers):
        #         should_list.append({
        #             "match": {
        #                 "filmography_si.role_name_si": "නළුවා"
        #             }
        #         })

        #     if(token in actress_identifers):
        #         should_list.append({
        #             "match": {
        #                 "filmography_si.role_name_si": "නිළිය"
        #             }
        #         })


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
                                                 "type": "most_fields",
                                                 "fields": ["real_name_si", "known_as_si",
                                                            "birth_si", "death_si",
                                                            "filmography_si.film_name_si",
                                                            "biography_si",
                                                            "national_awards_si.award_ceremony_name_si",
                                                            "national_awards_si.award_name_si",
                                                            "national_awards_si.film_name_si"],
                                                 "analyzer":"standard",   
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
