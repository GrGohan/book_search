import elasticsearch


class Search(object):
    def __init__(self, host, port, index):
        self.es = elasticsearch.Elasticsearch(host=host, port=port, )
        self.index = index

    def find_author(self, query):
        query_body = {
            "query": {
                "match": {
                    "author": f"{query}"
                }
            }
        }
        return self.es.search(index=self.index, body=query_body)

    def find_title(self, query):
        query_body = {
            "query": {
                "match": {
                    "title": f"{query}"
                }
            }
        }
        return self.es.search(index=self.index, body=query_body)

    def find_isbn(self, query):
        query_body = {
            "query": {
                "match": {
                    "isbn": f"{query}"
                }
            }
        }
        return self.es.search(index=self.index, body=query_body)
