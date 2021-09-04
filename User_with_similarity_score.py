import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

class DictList(dict):
    def __setitem__(self, key, value):
        try:
            # Assumes there is a list on the key
            self[key].append(value)
        except KeyError: # If it fails, because there is no key
            super(DictList, self).__setitem__(key, value)
        except AttributeError: # If it fails because it is not a list
            super(DictList, self).__setitem__(key, [self[key], value])

class UserWithSimilarityScore():
    
    def predict(self,user_id):
        user_info = pd.read_csv('User_data_with_matrix.csv')
        user_visit= pd.read_csv('user_visit_with_score.csv')
        post_detail=pd.read_csv('Data_posts_detail.csv')
        user_info = pd.DataFrame(user_info, columns = ['user_id','Male ','Female','अर्थ','सुरक्षा/अपराध','मनोरञ्जन','खेलकुद'])
        user_info.set_index('user_id', inplace=True)
        # Compute Cosine Similarity
        score= cosine_similarity(user_info, user_info)
        df = pd.DataFrame(score)

        df.to_excel(excel_writer = "score.xlsx")
        
        df= pd.read_csv('Socre_with_cosine_similatity.csv')
        # df = pd.DataFrame(pd.read_excel('score.xlsx'))
        print(df)
        # print(df.keys)
        
        _index=(df[df['Id']==user_id].index.tolist()[0])
        # print(_index.tolist()[0])
        # _index=df[df.columns['Id']==48].index
        print("INDEX IS "+str(_index))

        sorted_values = df.iloc[_index].sort_values(0, False)
        print('Top 5 row/values for the specific column:')
        top5 = sorted_values[1:6]
        print(top5)
        # print('Top 5 keys for the specific column:')
        keys = top5.keys()

        # print(keys)
        # user_visit
        user_visit.set_index('user_id', inplace=True)
        d = DictList()
        f = open("user_visit_with_score.csv")
        for line in f:
            line = line.strip('\n')
            (key, val) = line.split(",")
            d[key] = val
        
        # print(d)
        post_id_views=[d[k] for k in keys if k in d]
        # print(post_id_views)


        #Converting multidimensional list to single list
        flat_list = [x for list in post_id_views for x in list]
        print("FLAT")
        flat_list.sort()
        print(flat_list)
        
        #Removing Duplicates
        no_duplicate_list = list(set(flat_list))
        no_duplicate_list = list(map(int, no_duplicate_list))

        print(no_duplicate_list)

        #Converting multidimensional list to single list
        # mySet = []                   #declares an empty set
        # for list in post_id_views:             #loops over the items in myList          (for j in myList)
        #     for item in list:           #loops over the nested lists in myList   (for i in j)
        #         mySet.append(int(item))

        #removeing duplicate
        # res = []
        # for i in mySet:
        #     if i not in res:
        #         res.append(i)


        post_detail=post_detail.drop('post_date',axis=1)
        post_detail=post_detail.drop('post_content',axis=1)
        post_detail=post_detail.drop('category',axis=1)
        post_detail.reset_index(drop=True, inplace=True)

        print("Results")
        # maxlen= len(no_duplicate_list)
        # print(post_detail[post_detail['post_id']==4612])

        recommended=post_detail[post_detail['post_id'].isin(no_duplicate_list)]
        print(recommended)
        # for i in range(0,maxlen):
        #     print(post_detail["post_id"]==no_duplicate_list[i]])
            # print(post_detail[post_detail["post_id"] == no_duplicate_list[i]])
        
        # type(post_id_views[0][0])
        # print (post_detail[post_detail["post_id"] == 4612])
        return recommended


# predictor=UserWithSimilarityScore()
# predictor.predict(57)