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

class DataAnalyzer:
    #custom analyzer
    def custom_analyzer(self,text):
        words = regex.findall(r'\w{2,}', text) # at least 2 letters
        for w in words:
            yield w
            


class NewsPredictor:
    #prepare predictor based on combined features and historical records
    def prepare_predictor(self,df):
        self.df=df
        #count based vectors
        self.count_vect = CountVectorizer(analyzer = DataAnalyzer().custom_analyzer)
        #sparce matrix based on combined features
        self.sparse_matrix = self.count_vect.fit_transform(df["combined_features"])
        #document term matrix
        self.doc_term_matrix = self.sparse_matrix.todense()
        #dataframe for visualization
        self.dfs = pd.DataFrame(self.doc_term_matrix,columns=self.count_vect.get_feature_names(), )
        #calculate cosine similarity 
        self.cosine_sim=cosine_similarity(self.sparse_matrix)#dfs, dfs)

    #predict news list based on individual ID
    def predictById(self,id):
        recommended=[]
        index = (self.df[self.df['id']==str(id)].index)[0]
        similar_news = list(enumerate(self.cosine_sim[index]))
        sorted_similar = sorted(similar_news, key=lambda x:x[1], reverse=True)
        for news in sorted_similar[1:3]:
            index=int(news[0])
            print(index)
            similar=newsdb.get_news_from_index(index)
            recommended.append(similar)
        
        return recommended
        pass

    #bulk prediction
    def predict(self,history):  
        final_recommendation=set()
        for news in history:
            print(news['id'])
            items=self.prepare_result(news['id'])
            for item in items:
                final_recommendation.add(item)

        if len(final_recommendation)<1:
            return []
        else:
            return final_recommendation


    #prepare result for bulk pred.
    def prepare_result(self,post_id):
        recommended=[]
        index = (self.df[self.df['id']==str(post_id)].index)[0]
        similar_news = list(enumerate(self.cosine_sim[index]))
        sorted_similar = sorted(similar_news, key=lambda x:x[1], reverse=True)
        for news in sorted_similar[1:3]:
            index=int(news[0])
            print(index)
            similar=NewsDB().get_news_from_index(index)
            # print(type(similar))
            print(similar['title'])
            # print(similar['title'])
            recommended.append(similar)
            # recommended.append(NewsDB().get_news_from_index(index))
        return recommended
    pass


class NewsDB:
    #initialize news db
    def __init__(self) -> None:
        self.features = ['title']
        with open('db_full.json', 'r', encoding='utf-8') as datafile:
            data = json.load(datafile)
        self.df = pd.json_normalize(data['news'])
        self.df["combined_features"] = self.df.apply(self.combined_features, axis =1)
        #remove stop words
        print("REMOVING STOP WORDS")
        self.df['title']=self.df['title'].apply(lambda words: ' '.join(word.lower() for word in words.split() if word not in stopwords))
        print("REMOVED ALL STOP WORDS")
        pass

    def df(self):
        return self.df

    #get news from given ID
    def getNewsFromID(self,id):
        return self.df[self.df['id'] == id].values[0]

    #reset dataframe
    def resetFeatures(self):
        for feature in self.features:
            self.df[feature] = self.df[feature].fillna('')

    def remove_stop_words(self,source):
        sanitized=" ".join([x for x in source.split() if x not in stopwords])
        return sanitized


    #return combined features (apply content filtering here)
    def combined_features(self,row):
        return row['title']

    def get_title_from_index(self,index):
        return self.df[self.df.index == index]["title"].values[0]

    def get_news_from_index(self,index):
        return self.df[self.df.index == index].to_dict("records")[0]

    def get_news_from_id(self,id):
        return self.df[self.df['id'] == str(id)].to_dict("records")[0]

    def get_title_from_id(self,id):
        # print(id)
        return self.df[self.df['id']== str(id)]["title"].values[0]

    def get_index_from_title(self,title):
        return int(self.df[self.df.title == title]["id"].values[0])

    def get_index_from_id(self,id):
        return int(self.df[self.df.id == id]["id"].values[0])




class UserDB:
    #initialize users db
    def __init__(self) -> None:
        self.df_user_info=pd.read_csv("users_info.csv")
        self.df=pd.read_csv("user_visit.csv")
        pass

    #list users
    def getUsers(self):
        list = pd.DataFrame(self.df_user_info,  columns=["id","fullname","email"], )
        return list
    
    #get user's browsing history, perf. improvement possible
    def getUsersBrowsingHistory(self,user_id,newsdb):
        list = pd.DataFrame(self.df)
        item=list[list['user_id']==user_id]
        browsed=item['post_id'].values
        newslist=[]
        for id in browsed:
            newslist.append(newsdb.get_news_from_id(id))
        return newslist
    # print(item['post_id'].values)




newsdb=NewsDB()
predictor=NewsPredictor()
userdb=UserDB()


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
        history=userdb.getUsersBrowsingHistory(id,newsdb)
        self.wfile.write(json.dumps(history).encode())

    def do_RECOMMENDATION(self):
        self._set_json_headers()
        queryStrings=dict(urllib.parse.parse_qsl(self.path))
        print(queryStrings)
        id=int(queryStrings['/recommendation?id'])
        history=userdb.getUsersBrowsingHistory(id,newsdb)
        predictor.prepare_predictor(newsdb.df)
        lists=[]
        for item in history:
            print(item['id'])
            predicted=predictor.predictById(item['id'])
            for __ in predicted:
                lists.append(__)

       
        
        self.wfile.write(json.dumps(lists).encode())


    def do_USER(self):
        self._set_json_headers()
        userdb=UserDB()
        users=userdb.getUsers().to_dict("records")
        # print(users)
        # users=[{'fullname':"RAM",'id':20},{'fullname':"Shyam",'id':30}]
        self.wfile.write(json.dumps(users).encode())

        
    def do_GET(self):
        print(self.path)
        if self.path=='/':
             self.__set_html_headers()
             self.path = 'index.html'
             return SimpleHTTPRequestHandler.do_GET(self)
        elif self.path.startswith('/recommendation'):
             self.do_RECOMMENDATION()
        elif self.path=='/users':
            self.do_USER()
        elif self.path.startswith("/history"):
            self.do_HISTORY()
        else:
            pass
            #  links=[1,2,3]
            #  self.wfile.write(json.dumps(links).encode())
            #  print(urllib.parse.parse_qs(self.path))



def run(server_class=HTTPServer, handler_class=Server, port=4444):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print('Starting http server on port %d...', port)
    print("Please open browser on specific port")
    httpd.serve_forever()
    


run()



       
