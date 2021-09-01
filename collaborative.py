import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import operator

class NewsRecommendationCollaborative:
    def __init__(self) -> None:
        #user visit csv load garne
        self.similar_users=[]
        self.similar_news=[]

        self.visits_data=pd.read_csv("user_visit.csv")
        self.news_data=pd.read_json("db_full.json")
        self.newslist = pd.json_normalize(self.news_data['news'])

        #dataframe ma convert garne
        self.visits=pd.DataFrame(self.visits_data)
        #visited bhanne column thapne , for simplicity
        self.visits['visited']=1
        #print garne for visualization
        print(self.visits.head())
        print(self.newslist.head())                
        pass
    
    def content_summary(self):
        #unique users count
        print("Unique Users:"+str(len(self.visits['user_id'].unique())))
        #unique visits count
        print("total Visits:"+str(len(self.visits)))
        #unique news count
        print("Unique news:"+str(len(self.newslist['id'].unique())))
        pass

    def user_mapping_filtering(self):
        visits_per_user = self.visits.groupby('user_id')['visited'].count()
        # print(self.visits_per_user) 
        self.visits_per_user_df = pd.DataFrame(visits_per_user)
        #filter if user has visited less than 3 news
        self.filtered_visits_per_user_df = self.visits_per_user_df[self.visits_per_user_df.visited > 3]
        print(self.filtered_visits_per_user_df) #user id=row,visit_count=column
        sorted_visits=self.filtered_visits_per_user_df.sort_values("visited")
        # print("SORTED__START")
        # print(sorted_visits)
        # print("SORTED__END")
        self.active_users = sorted_visits.index.tolist()
        #active users in list
        print("ACTIVE USERS")
        print(self.active_users)


    def news_mapping_filtering(self):
        self.visits_per_news = self.visits.groupby('post_id')['visited'].count()
        # print(self.visits_per_news) #news id=row,visit_count=column
        #visit per news ko dataframe
        self.visits_per_news_df = pd.DataFrame(self.visits_per_news)
        print(self.visits_per_news_df)
        # remove if < 2 views
        filtered_visits_per_news_df = self.visits_per_news_df[self.visits_per_news_df.visited >= 2]
        # #list ma convert gareko >2 views bhako news lai
        self.popular_news = filtered_visits_per_news_df.index.tolist()
        print(self.popular_news)

    def user_news_common_mapping(self):
        #based on popular news
        self.filtered_visits = self.visits[self.visits.post_id.isin(self.popular_news)]
        print("FILTERED VISITS BASED ON POPULAR NEWS")
        print(self.filtered_visits)
        #based on active users
        self.filtered_visits = self.visits[self.visits.user_id.isin(self.active_users)]
        print("FILTERED VISITS BASED ON ACTIVE USERS")
        print((self.filtered_visits))
    
    def prepare_visitor_matrix(self):
        #rows=user_id,col=post_id based on visited
        self.visits_matrix = self.filtered_visits.pivot_table(index='user_id', columns='post_id', values='visited')
        # replace NaN values with 0
        self.visits_matrix = self.visits_matrix.fillna(0)
        # display the top few rows
        print("VISIT MATRIX WITH NON USEFUL DATA REMOVED")
        print(self.visits_matrix)

    def prepare_similar_users(self,user_id, visited_matrix):
        #get user
        user = visited_matrix[visited_matrix.index == user_id]
        print(user)
        #get other users
        other_users = visited_matrix[visited_matrix.index != user_id]
        other_user_index=other_users.index.tolist()
        #find cosine sim. between user and other users 
        #pahilo row lai list banaam, it has cosine sim list
        similarities = cosine_similarity(user,other_users)[0].tolist()
        print("COSINE SIMILARITY LIST")
        print(similarities)
        #user ra similarity ko key value pair banaam 
        user_other_similarity = dict(zip(other_user_index, similarities))
        print("SIMILARITY KEY VALUE PAIR WITH OTHER USERS")
        print(user_other_similarity)
        #sort garne, mathiko similarity lai , reversed order maa high->low
        user_other_similarity_sorted = sorted(user_other_similarity.items(), key=operator.itemgetter(1))
        user_other_similarity_sorted.reverse()
        print("SIMILARITY WITH USERS , SORTED")
        print(user_other_similarity_sorted)
        #top 5 matra line
        top_users_similarities = user_other_similarity_sorted[:5]
        #key value pair bata key or user_id matra tanne
        self.similar_users_list = [u[0] for u in top_users_similarities]
        print("SIMILAR USERS")
        print(self.similar_users_list)

    def prepare_users_visited_news(self):
        similar_users_visit_history = self.visits_matrix[self.visits_matrix.index.isin(self.similar_users_list)]
        print("SIMILAR USERS POST VISIT DATAFRAME")
        print(similar_users_visit_history)
        similar_users_visit_history_mean = similar_users_visit_history.mean(axis=0)
        print("SIMILAR USERS VISIT HISTORY BY MEAN VISITS")
        print(similar_users_visit_history_mean)
        #mathiko lai meanko basis ma dataframe banaam
        similar_users_visit_hisotry_df=pd.DataFrame(similar_users_visit_history_mean,columns=['mean'])
        print("SIMILAR USERS VISIT HISTORY DATAFRAME")
        print(similar_users_visit_hisotry_df)
        #sort dataframe based on high means > low means
        self.similar_users_visit_history_df_ordered = similar_users_visit_hisotry_df.sort_values(by=['mean'], ascending=False)
        print("SIMILAR USERS VISIT HISTORY DF ORDERED")
        print(self.similar_users_visit_history_df_ordered)

    def user_visited_news_history(self,user_id):
        user_history = self.visits[self.visits['user_id']==user_id]
        # print(user_history)
        user_history_posts=user_history['post_id'].tolist()
        user_history_posts = map(str, user_history_posts) 
        visit_history=self.newslist[self.newslist['id'].isin(user_history_posts)]
        print("USER POST VISIT HISTORY")
        print(visit_history)

    def predict_news(self):
        #most matched news 5 ota ligne
        top_news = self.similar_users_visit_history_df_ordered.head(5)
        print("MOST MATCHED TOP 5 NEWS")
        print(top_news)
        #listma convert garne
        top_n_news_items = top_news.index.tolist()
        print(top_n_news_items)
        #as id in string format in db,converting to string for comparison
        list_string = map(str, top_n_news_items) 
        #find the news from newslist, which are in above id list 
        self.similar_news = self.newslist[self.newslist['id'].isin(list_string)]
        print("PREDICTED NEWS")
        print(self.similar_news)

    
 


predictor=NewsRecommendationCollaborative() 
predictor.content_summary()
predictor.user_mapping_filtering()
predictor.news_mapping_filtering()
predictor.user_news_common_mapping()
predictor.prepare_visitor_matrix()
predictor.prepare_similar_users(66,predictor.visits_matrix)
predictor.prepare_users_visited_news()
predictor.user_visited_news_history(66)
predictor.predict_news()
