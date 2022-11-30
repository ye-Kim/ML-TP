import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics.pairwise import cosine_similarity

#data preprocessing
data = './data/data.csv'
df = pd.read_csv(data)
df_food = pd.read_csv('./data/food_unit.csv')

def get_need_kcal(hei, exer, gender):
    hei = hei / 100

    if gender == 'Male':
        need = hei * hei * 22
    elif gender == 'Female':
        need = hei * hei * 21

    if exer == 0: #low exercise
        need = need * 25
    elif exer == 1: #middle exercise
        need = need * 30
    elif exer == 2: #high exercise
        need = need * 35
    
    return round(need, -2)

need_cal = []

for i in range(10000):
    hei = df.iloc[i, 3]
    exer = df.iloc[i, 0]
    gender = df.iloc[i, 1]

    need = get_need_kcal(hei, exer, gender)
    need_cal.append(need)

df['need'] = need_cal

groups = df.groupby(df.Gender)
df_male = groups.get_group('Male')
df_female = groups.get_group('Female')

#content-based filtering
foodli = list(df_food['식품군'].unique())

#food unit data per need kcal
need_cal = list(set(df['need']))
need_cal.sort()

grain = [5,5,6,6,7,7,8,8,8,9,10,10,10,11,11,11,11,11,11]
fm = [3,4,4,4,4,5,5,5,5,5,5,6,7,7,8,8,8,10,10]
vege = [3,3,3,5,6,6,7,7,7,7,7,8,8,8,8,8,8,8,9]
fat = [2,3,3,4,4,4,4,4,4,4,4,5,5,6,6,7,7,7,8]
milk = [1,1,1,1,1,1,1,2,2,2,2,2,2,2,2,2,3,3,3]
fruit = [1,1,1,1,1,1,1,1,2,2,2,2,2,2,2,3,3,3,3]
need_list = [grain, fm, vege, fat, milk, fruit]

kcal_need = pd.DataFrame(need_cal, columns=['need_kcal'])

for li in foodli:
    kcal_need[li] = need_list[foodli.index(li)]

#base recommendated diet
food_g = df_food.groupby('식품군')

base_recom = pd.DataFrame(columns=foodli)
recom_li = []

for li in foodli:
    f = food_g.get_group(li)
    recom_li.append(f.iloc[0,0])

base_recom.loc[0] = recom_li

#random change recommendation in each food unit
import random

for li in foodli:
    f = food_g.get_group(li)
    i = random.randrange(len(f))
    base_recom.iloc[0, foodli.index(li)] = f.iloc[i, 0]

#collaborative filtering
#merge like/hate food data
like_df = df[['Like_1', 'Hate_1']]
hate_df = df[['Like_1', 'Hate_1']]

like_df.drop(['Hate_1'], axis=1, inplace=True)
hate_df.drop(['Like_1'], axis=1, inplace=True)
like_df['score'] = 10
hate_df['score'] = 0

li = []
for i in range(10000):
    li.append(i)

like_df['Index'] = li
hate_df['Index'] = li

like_df.rename(columns={'Like_1':'Food'}, inplace=True)
hate_df.rename(columns={'Hate_1':'Food'}, inplace=True)

df_food.drop(['용량(g)'], axis=1, inplace=True)
df_food.rename(columns={'품목':'Food'}, inplace=True)

like = pd.merge(like_df, df_food, on='Food', how='left')
hate = pd.merge(hate_df, df_food, on='Food', how='left')

like_hate = pd.concat([like, hate])

#calculate rating(preference)
#0: hate, 5: soso, 10: like

food = like_hate.pivot_table('score', index='Food', columns='Index')
food.fillna(5, inplace=True)

#calculate cosine similarity
item_base_colla = cosine_similarity(food)

#calculate preferences(similarity) of each food
item_base_colla_df = pd.DataFrame(data=item_base_colla, index=food.index, columns=food.index)

def get_food_unit(food):
    return df_food[df_food['Food']==food].iloc[0, 1]

def get_item_colla_like(Food):
    unit = get_food_unit(Food)
    same_unit = []

    for i in range(len(df_food[df_food['식품군']==unit])):
        same_unit.append(df_food[df_food['식품군']==unit].iloc[i, 0])

    same_unit_df = item_base_colla_df[same_unit].loc[same_unit]
    return same_unit_df[Food].sort_values(ascending=False)[:2].index[1]
    #in descending sort, first feature is itself (similarity: 1)

def get_item_colla_hate(Food):
    #in hate df, the lowest similarity might be the highest preference
    unit = get_food_unit(Food)
    same_unit = []

    for i in range(len(df_food[df_food['식품군']==unit])):
        same_unit.append(df_food[df_food['식품군']==unit].iloc[i, 0])

    same_unit_df = item_base_colla_df[same_unit].loc[same_unit]
    return same_unit_df[Food].sort_values(ascending=True)[:1].index[0]

#get result

def get_recom(data, recom):
    exer = data[0]
    gender = data[1]
    height = data[2]
    like = data[4]
    hate = data[5]

    #collaborative filtering
    li_recom = get_item_colla_like(like)
    ha_recom = get_item_colla_hate(hate)
    
    col = foodli.index(get_food_unit(like))
    recom.iloc[0, col] = li_recom

    col = foodli.index(get_food_unit(hate))
    recom.iloc[0, col] = ha_recom

    #calculate need kcal
    need = get_need_kcal(height, exer, gender)

    need_li = list(kcal_need[kcal_need['need_kcal']==need].iloc[0, 1:])
    need_li = list(map(int, need_li))
    recom.loc[1] = need_li

    #calculate food volumes    
    df_fu = pd.read_csv('./data/food_unit.csv')

    for i in range(len(recom.columns)):
        food = recom.iloc[0, i]
        food_unit = df_fu[df_fu['품목']==food].iloc[0, 1]
        vol = food_unit * recom.iloc[1, i]
        recom.iloc[1, i] = vol

    return recom

def print_result(data, recom):
    recom = get_recom(data, recom)
    print('The need of kcal:', str(need), '(kcal)')

    print('==Recommendation Diet==')
    for i in range(len(recom.columns)):
        print(str(recom.columns[i]), ':', str(recom.iloc[0, i]), str(recom.iloc[1, i]), 'g')


#exercise, gender, height, weight, like, hate
test_data = input('Please enter /exercise/gender/height/weight/like/hate/')

print_result(test_data, base_recom)