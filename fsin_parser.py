#!/usr/bin/env python
# coding: utf-8

import flask
import simplejson as json
import sqlite3 as lite
import requests
from lxml import html
from lxml.html.diff import htmldiff
import HTMLParser
from datetime import datetime
import time
import threading

class WebApplication:
    def __init__(self):
        self.app = flask.Flask(__name__, static_url_path = '')
        self.fsin_parser = FsinParser()

        @self.app.route('/js/<path:path>')
        def send_js(path):
            return flask.send_from_directory('js', path)

        @self.app.route('/', methods = ['GET'])
        def start_page():
            return self.app.send_static_file('index.html')

        @self.app.route('/get_url_list', methods = ['POST'])
        def get_url_list():
            print self.fsin_parser.get_pages_list()
            return json.dumps(self.fsin_parser.get_pages_list())

        @self.app.route('/rm_url_from_list', methods = ['POST'])
        def rm_url_from():
            try:
                self.fsin_parser.delete_url_from_pages_list(int(flask.request.form['id']))
                return 'OK'
            except:
                return 'FAIL'

        @self.app.route('/add_url', methods = ['POST'])
        def add_url():
            self.fsin_parser.put_url_to_pages_list(flask.request.form['url'])
            return 'OK'

        @self.app.route('/get_updates', methods = ['POST'])
        def get_updates():
            ans = self.fsin_parser.get_updates(flask.request.form['date_begin'], flask.request.form['date_end'])
            return json.dumps(ans)

        @self.app.route('/get_update_by_id_and_dates', methods = ['POST'])
        def get_update_by_id_and_dates():
            ans = self.fsin_parser.get_update_by_id_and_dates(int(flask.request.form['id']), flask.request.form['date_begin'], flask.request.form['date_end']) 
            return ans

        @self.app.route('/get_status_string', methods = ['POST'])
        def get_status_string():
            return self.fsin_parser.status_string

        @self.app.route('/set_readed', methods = ['POST'])
        def set_readed():
            self.fsin_parser.set_readed(int(flask.request.form['id']))
            return 'OK'

        d = threading.Thread(target = self.fsin_parser.thread_function)
        d.setDaemon(True)
        d.start()

    def run(self):
        self.app.run(host = '0.0.0.0')

class FsinParser:
    def __init__(self):
        self.json_name = '1.json'
        with open(self.json_name, 'r') as f:
            self.json = json.load(f)
            f.close()
        self.db = lite.connect(self.json['db_name'], check_same_thread = False)
        self.db.text_factory = str
        self.cursor = self.db.cursor()
        self.status_string = 'сканирование запущено'
        try:
            self.cursor.executescript("""
                CREATE TABLE IF NOT EXISTS PAGES_HISTORY (
                    Id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Page INT,
                    Data STRING,
                    Time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    Readed BOOL DEFAULT FALSE
                );""")
            self.cursor.executescript("""
                CREATE TABLE IF NOT EXISTS PAGES_LIST (
                    Id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Url STRING NOT NULL,
                    LastUpdate TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );""")
        except lite.Error as e:
            print '__init__: SQL Error', e
        self.pages_list = self.get_pages_list()

    def thread_function(self):
        while True:
            self.update_pages_history()
            time.sleep(3600)

    def __del__(self):
        if (self.db):
            self.db.close()

    def get_pages_list(self):
        try:
            self.cursor.execute("SELECT Id, Url, LastUpdate FROM PAGES_LIST")
            res = [{"id": x[0], "url": x[1], "last_update": x[2]} for x in self.cursor.fetchall()]
            return res
        except lite.Error as e:
            print 'get_pages_list: SQL Error', e

    def put_url_to_pages_list(self, url):
        try:
            self.cursor.execute("INSERT INTO PAGES_LIST (Url) VALUES(?)", (url,))
            self.db.commit()
        except lite.Error as e:
            print ': SQL Error', e

    def delete_url_from_pages_list(self, url_id):
        try:
            self.cursor.execute("DELETE FROM PAGES_LIST WHERE Id=?", (url_id,))
            self.db.commit()
        except lite.Error as e:
            print ': SQL Error', e

    def get_page_from_internet(self, url):
        try:
            page = requests.get(url)
            tree = html.document_fromstring(page.content)
            info = tree.xpath(self.json['xpath_request'])[0]
            return HTMLParser.HTMLParser().unescape(html.tostring(info)).encode('utf-8')
        except Exception as e:
            print 'parser: Error', e
     
    def update_pages_history(self):
        self.pages_list = self.get_pages_list()
        for page in self.pages_list:
            try:
                page_id = page['id']
                new_page = self.get_page_from_internet(page['url'])
                self.cursor.execute("SELECT Id, Data FROM PAGES_HISTORY WHERE Page=? ORDER BY datetime(Time) DESC LIMIT 1", (page_id,))
                old_page_entry = self.cursor.fetchall()
                if len(old_page_entry) == 0 or (len(old_page_entry) != 0 and old_page_entry[0][1] != new_page):
                    self.cursor.execute("INSERT INTO PAGES_HISTORY (Page, Data) VALUES(?, ?)", (page_id, new_page))
                    self.db.commit()
		self.status_string = 'Последняя ссылка просканирована ' + str(datetime.now()) + ' (' + page['url'] + ')'
            except lite.Error as e:
                print ': SQL Error', e
    
    def get_updates(self, date_begin, date_end):
        t = self.make_between_dates(date_begin, date_end)
        print t
        try:
            #self.cursor.execute("SELECT Id, Page, Time, Readed FROM PAGES_HISTORY WHERE ? ORDER BY Page", 
            #                    (self.make_between_dates(date_begin, date_end),))
            self.cursor.execute("SELECT Id, Page, Time, Readed FROM PAGES_HISTORY WHERE " + t + " ORDER BY Readed, Time DESC") 

            id_list = self.cursor.fetchall()
            print id_list
            ans = [{"id": x[0], "page": x[1], "time": x[2], "readed": x[3]} for x in id_list]
            return ans
        except lite.Error as e:
            print "SQL error", e
    
    def get_update_by_id_and_dates(self, url_id, date_begin, date_end):
        try:
            t = self.make_between_dates(date_begin, date_end)
            self.cursor.execute("SELECT * FROM PAGES_HISTORY WHERE " + t + " AND (Page=?) ORDER BY Id", 
                                (url_id,))
            entries = self.cursor.fetchall()
            diff = self.get_diff_of_pages(entries[0][2], entries[-1][2])
            return diff
        except Exception as e:
            print "SQL Error", e


    def make_between_dates(self, date_begin, date_end):
        # dates if not nil must be in format 'YYYY-MM-DD HH:MM:SS[.mmmmmm]' - [] means that milliseconds may be ommited
        try:
            date_begin = date_begin.strip()
            date_end = date_end.strip()
            if date_begin == "" and date_end == "":
                return "1"
            if date_begin == "" or date_end == "":
                return "(Time > %s)" % (date_begin + date_end)
            if date_begin > date_end:
                date_begin, date_end = date_end, date_begin
            return "(Time BETWEEN '%s' AND '%s')" % (date_begin, date_end)
        except Exception as e:
            print "ERR", e
            return "1"

    def set_readed(self, url_id):
        try:
            self.cursor.execute("UPDATE PAGES_HISTORY SET Readed='TRUE' WHERE Page=?", (url_id,))
            self.db.commit()
        except Exception as e:
               print "SQL Error", e

    def get_diff_of_pages(self, page1, page2):
        diff = HTMLParser.HTMLParser().unescape(htmldiff(page1.decode('utf-8'), page2.decode('utf-8')).encode('utf-8'))
        diff = diff.replace('<del>', '<del style="color:red">')
        diff = diff.replace('<ins>', '<ins style="color:green">')
        return HTMLParser.HTMLParser().unescape(diff)
    
    def finish(self):
        if (self.db):
            self.db.close()
        
    

if __name__ == '__main__':
    app = WebApplication()
    app.run()
    #parser = FsinParser()
    #parser.get_update_by_id_and_dates(4, '01.01.00', '01.01.20')
    #parser.delete_url_from_pages_list(0)
    #parser.update_pages_history()
    #parser.put_url_to_pages_list('http://48.fsin.su/structure/ispravitelnaya-koloniya-2.php')
    #parser.put_url_to_pages_list('http://www.30.fsin.su/structure/detail.php?ELEMENT_ID=33807')

    #print parser.pages_list
    #with open('out1.txt', 'w') as f:
    #    f.write(parser.get_info_from_page(0))
    #    f.close()

