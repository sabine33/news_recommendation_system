#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
user_info = pd.read_csv('/Users/surajshrestha/Downloads/User_data_with_matrix.csv')
user_visit= pd.read_csv('/Users/surajshrestha/Downloads/Data_user_visit.csv')
post_detail=pd.read_csv('/Users/surajshrestha/Downloads/Data_posts_detail.csv')


# In[2]:


user_visit=user_visit.drop('SN.',axis=1)


# In[3]:


user_visit.head()


# In[4]:


post_detail.head()


# In[5]:


user_info.head()


# In[6]:


user_info = pd.DataFrame(user_info, columns = ['user_id','Male ','Female','अर्थ','सुरक्षा/अपराध','मनोरञ्जन','खेलकुद'])


# In[7]:


user_info


# In[8]:


user_info.set_index('user_id', inplace=True)


# In[9]:


user_info


# In[10]:


#Claculating the cosine score for user_id for 48
# Compute Cosine Similarity

from sklearn.metrics.pairwise import cosine_similarity
print(cosine_similarity(user_info, user_info))


# In[125]:



score= cosine_similarity(user_info, user_info)

df = pd.DataFrame(score).T
df.to_excel(excel_writer = "/Users/surajshrestha/Downloads/score.xlsx")


# In[ ]:





# In[107]:


user_info.head(13)


# In[11]:


#Score_Cosine_similarity
df= pd.read_csv('/Users/surajshrestha/Downloads/Socre_with_cosine_similatity.csv')


# In[12]:


df


# In[199]:


M = df['48'].to_numpy()
M


# In[190]:


M.sort()


# In[200]:


M[-1],M[-2],M[-3],M[-4]


# In[203]:


sampledata= df.iloc[0,[1]]
sampledata.sort_values(by="48")


# In[204]:


similar_user = list(enumerate(df[id]))


# In[16]:


import pandas as pd

df = pd.DataFrame(pd.read_csv('/Users/surajshrestha/Downloads/Socre_with_cosine_similatity.csv'))

sorted_values = df.iloc[2].sort_values(0, False)
print('Top 5 row/values for the specific column:')
top5 = sorted_values[1:6]
print(top5)
print('Top 5 keys for the specific column:')
keys = top5.keys()
print(keys)
print("===============")
#print("Tuple and the respective values: ")
#for key in keys:
 #   print(('48', key), "=" , top5.get(key))


# In[ ]:




