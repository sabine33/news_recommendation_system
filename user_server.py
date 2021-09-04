from User_with_similarity_score import UserWithSimilarityScore
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

class UserDB:
    #initialize users db
    def __init__(self) -> None:
        self.df_user_info=pd.read_csv("users_info.csv")
        self.visits=pd.read_csv("user_visit.csv")
        self.newslist=pd.read_csv("Data_posts_detail.csv")
        self.newslist = self.newslist.fillna("NAN")
        
        pass
    
    def user_visited_news_history(self,user_id):
        user_history = self.visits[self.visits['user_id']==user_id]
        print(user_history)
        user_history_posts=user_history['post_id'].tolist()
        # print(user_history_posts)
        # user_history_posts = list(map(str, user_history_posts))
        
        visit_history=self.newslist[self.newslist['post_id'].isin(user_history_posts)]
        
        print("USER POST VISIT HISTORY")
        # print(visit_history)
        return visit_history

    #list users
    def getUsers(self):
        return self.df_user_info
       
    #get user's browsing history, perf. improvement possible
    def getUsersBrowsingHistory(self,user_id):
        list = pd.DataFrame(self.df)
        item=list[list['user_id']==user_id]
        browsed=item['post_id'].values
        newslist=[]
        for id in browsed:
            newslist.append(self.newsdb.get_news_from_id(id))
        return newslist

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
        history=UserDB().user_visited_news_history(id)
        # print(history)
        json_list = json.loads(json.dumps(list(history.T.to_dict().values())))
        print(json_list)
        self.wfile.write(json.dumps(json_list).encode())

    def do_RECOMMENDATION(self):
        self._set_json_headers()
        queryStrings=dict(urllib.parse.parse_qsl(self.path))        
        id=int(queryStrings['/recommendation?id'])
        recommendation=UserWithSimilarityScore().predict(id)
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
             self.path = 'user.html'
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

