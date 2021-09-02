from collaborative import NewsRecommendationCollaborative, UserDB
from http.server import SimpleHTTPRequestHandler, HTTPServer
import json
import re
import urllib.parse
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import regex
from stopwords import stopwords

#http server to serve the resource
class Server(SimpleHTTPRequestHandler):
    def _set_json_headers(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-type', 'application/json')
        self.end_headers()
    
    def __set_html_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.send_header('Access-Control-Allow-Origin', '*')
        # self.end_headers()
        
    def do_HEAD(self):
        self._set_headers()

    def do_HISTORY(self):
        self._set_json_headers()
        queryStrings=dict(urllib.parse.parse_qsl(self.path))
        print(queryStrings)
        id=int(queryStrings['/history?id'])
        predictor=NewsRecommendationCollaborative() 
        history=predictor.user_visited_news_history(id)
        print(history)
        json_list = json.loads(json.dumps(list(history.T.to_dict().values())))
        print(json_list)
        self.wfile.write(json.dumps(json_list).encode())

    def do_RECOMMENDATION(self):
        self._set_json_headers()
        queryStrings=dict(urllib.parse.parse_qsl(self.path))
        
        print(queryStrings)
        id=int(queryStrings['/recommendation?id'])
        predictor=NewsRecommendationCollaborative() 
        predictor.content_summary()
        predictor.user_mapping_filtering()
        predictor.news_mapping_filtering()
        predictor.user_news_common_mapping()
        predictor.prepare_visitor_matrix()
        predictor.prepare_similar_users(id,predictor.visits_matrix)
        predictor.prepare_users_visited_news()
        predictor.user_visited_news_history(id)
        recommendation=predictor.predict_news(id)
        json_list = json.loads(json.dumps(list(recommendation.T.to_dict().values())))
        # print(json_list)
        self.wfile.write(json.dumps(json_list).encode())


    def do_USER(self):
        self._set_json_headers()
        users=UserDB().getUsers()
        json_list = json.loads(json.dumps(list(users.T.to_dict().values())))
        # users=[{'fullname':"RAM",'id':20},{'fullname':"Shyam",'id':30}]
        self.wfile.write(json.dumps(json_list).encode())

        
    def do_GET(self):
        print(self.path)
        if self.path=='/':
             self.__set_html_headers()
             self.path = 'collab.html'
             return SimpleHTTPRequestHandler.do_GET(self)
        elif self.path.startswith('/recommendation'):
             self.do_RECOMMENDATION()
        elif self.path=='/users':
            self.do_USER()
        elif self.path.startswith("/history"):
            self.do_HISTORY()
        else:
            pass



def run(server_class=HTTPServer, handler_class=Server, port=4444):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print('Starting http server on port %d...', port)
    print("Please open browser on specific port")
    httpd.serve_forever()
    

# UserDB().getUsers()

run()

