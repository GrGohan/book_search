# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

from scrapy.utils.project import get_project_settings
from elasticsearch import Elasticsearch



class ElasticDBPipeline:
    def __init__(self):
        self.settings = get_project_settings()
        self.es = Elasticsearch([{'host': self.settings.get("ES_SERVER"), 'port': self.settings.get('ES_PORT')}])
        self.create_index()


    def create_index(self):
        try:
           if not self.es.indices.exists(self.settings.get("ES_DOC")):
               self.es.indices.create(index=self.settings.get("ES_DOC"), ignore=400)


        except Exception as e:
            print(e)


    def process_item(self, item, spider):
        try:
            self.es.index(index=self.settings.get("ES_DOC"), body=dict(item), id=item["hash"])
        except Exception as e:
            print(e)


