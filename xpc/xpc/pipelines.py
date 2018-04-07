# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql

class MysqlPipeline(object):
    def __init__(self):
        self.conn = None
        self.cur = None

    def open_spider(self, spider):
        self.conn = pymysql.connect(
            host='127.0.0.1',
            port=3306,
            user='root',
            password='rock1204',
            db='xpc',
            charset='utf8'

        )
        self.cur = self.conn.cursor()

    def process_item(self, item, spider):
        if not hasattr(item, 'table_name'):
            return item
        cols, values = zip(*item.items())
        sql = "INSERT INTO `%s` (%s) VALUES (%s)" % \
              (item.table_name, ','.join(cols), ','.join(['%s'] * len(values)))
        self.cur.execute(sql, values)
        print('*' * 50)
        self.conn.commit()

        return item
    def close_spider(self,spider):

        self.cur.close()
        self.conn.close()