from flask import Flask, render_template
from elasticsearch import Elasticsearch, helpers

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html", title="Sinhala Artist Search")
if __name__ == "__main__":
    app.run()