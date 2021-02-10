from flask import (
    Flask,
    render_template,
    request,
    jsonify
)
import es_engine, config
from flask_wtf.csrf import CSRFProtect


app = Flask(__name__)
app.config["DEBUG"] = True
csrf = CSRFProtect(app)
es = es_engine.Search(config.ES_HOST, config.ES_PORT, config.ES_INDEX)

def run(host, port):
    app.run(host, port)


@app.route("/author/<query>", methods=["GET"])
def search_author(query):
    return es.find_author(query)["hits"]


@app.route("/title/<query>", methods=["GET"])
def search_title(query):
    return get_info(es.find_title(query)["hits"])


@app.route("/isbn/<query>", methods=["GET"])
def search_isbn(query):
    return get_info(es.find_isbn(query)["hits"])

def get_info(info):
    res = []
    for item in info["hits"]:
        res.append(item["_source"])
    return jsonify(res)

@app.route('/', methods=['GET'])
def home():
    return render_template("index.html")


