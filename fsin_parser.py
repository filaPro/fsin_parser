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

        d = threading.Thread(name='daemon', target=self.fsin_parser.update_pages_history)
        d.setDaemon(True)

    def run(self):
        self.app.run()

class FsinParser:
    def __init__(self):
        self.json_name = '1.json'
        with open(self.json_name, 'r') as f:
            self.json = json.load(f)
            f.close()
        self.db = lite.connect(self.json['db_name'], check_same_thread = False)
        self.db.text_factory = str
        self.cursor = self.db.cursor()
        try:
            self.cursor.executescript("CREATE TABLE IF NOT EXISTS PAGES_HISTORY(Id INT, Info STRING, Datetime DATETIME);")
            self.cursor.executescript("CREATE TABLE IF NOT EXISTS PAGES_LIST(Id INT, Url STRING);")
        except:
            print '__init__: SQL Error'
        self.pages_list = self.get_pages_list()

    def thread_function(self):
        while True:
            self.update_pages_history()
            time.sleep(6000)

    def __del__(self):
        if (self.db):
            self.db.close()

    def get_pages_list(self):
        try:
            self.cursor.execute("SELECT * FROM PAGES_LIST")
            return self.cursor.fetchall()
        except:
            print 'get_pages_list: SQL Error'

    def put_url_to_pages_list(self, url):
        try:
            max_id = -1
            for page in self.pages_list:
                if (page[0] > max_id):
                    max_id = page[0]
            max_id += 1
            self.cursor.execute("INSERT INTO PAGES_LIST VALUES(?, ?)", (max_id, url))
            self.db.commit()
        except:
            print ': SQL Error'

    def delete_url_from_pages_list(self, url_id):
        try:
            self.cursor.execute("DELETE FROM PAGES_LIST WHERE Id=?", (url_id,))
            self.db.commit()
        except:
            print ': SQL Error'

    def get_page_from_internet(self, url):
        try:
            page = requests.get(url)
            tree = html.document_fromstring(page.content)
            info = tree.xpath(self.json['xpath_request'])[0]
            return HTMLParser.HTMLParser().unescape(html.tostring(info)).encode('utf-8')
        except:
            print ': Error'
     
    def update_pages_history(self):
        self.pages_list = self.get_pages_list()
        for page in self.pages_list:
            try:
                page_id = page[0]
                new_page = self.get_page_from_internet(page[1])
                self.cursor.execute("SELECT * FROM PAGES_HISTORY WHERE Id=? ORDER BY datetime(Datetime) DESC LIMIT 1", (page_id,))
                old_page_entry = self.cursor.fetchall()
                if len(old_page_entry) == 0 or (len(old_page_entry) != 0 and old_page_entry[0][1] != new_page):
                    self.cursor.execute("INSERT INTO PAGES_HISTORY VALUES(?, ?, ?)", (page_id, new_page, datetime.now()))
                    self.db.commit()
            except:
                print ': SQL Error'
    
    def get_updates(self, date_begin, date_end):
        self.cursor.execute("SELECT Id FROM PAGES_HISTORY WHERE Datetime BETWEEN ? AND ? ORDER BY Id", 
                            (datetime.strptime(date_begin, '%d.%m.%y'), datetime.strptime(date_end, '%d.%m.%y')))
        id_list = self.cursor.fetchall()
        cur_id = 0
        ans = []
        for i in xrange(1, len(id_list)):
            if id_list[i][0] == id_list[i - 1][0] and id_list[i][0] > cur_id:
                ans.append(id_list[i][0])
                cur = id_list[i][0]
        return ans
    
    def get_update_by_id_and_dates(self, url_id, date_begin, date_end):
        self.cursor.execute("SELECT * FROM PAGES_HISTORY WHERE (Datetime BETWEEN ? AND ?) AND (Id=?) ORDER BY Id", 
                            (datetime.strptime(date_begin, '%d.%m.%y'), datetime.strptime(date_end, '%d.%m.%y'), url_id))
        entries = self.cursor.fetchall()
        diff = self.get_diff_of_pages(entries[0][1], entries[-1][1])
        return diff
        
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

