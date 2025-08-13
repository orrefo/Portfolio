import pandas as pd
import numpy as np
import Levenshtein
import requests
import time


print('finished requirements upload')
def score(x):
    return round(((107.3 * x ** (-0.402)))+(-15.79*np.log(x+1)+88.06),0)/2


def load_data(name,bool): #return Cleaned DataFrame with duplicates removed
    if bool==True:
        data= pd.read_csv(name+'.csv',index_col=0)
    else:
        data= pd.read_csv(name+'.csv')    
    data= data.drop_duplicates()
    return data

def merge_track(table_1,table_2): #Merge two DataFrames on 'track_id' column using a left join.
    data=pd.merge(table_1,table_2,left_on='track_id',right_on='track_id',how='left')
    return data

def merge_artist(table_1,table_2):
    data=pd.merge(table_1,table_2,left_on='artist_id',right_on='artist_id',how='left')
    return data

# Load datasets
chart=load_data('chart',True)
mapping=load_data('mapping',True)
artist=load_data('artist',True)
tracks=load_data('tracks',True)

# Ensure mapping file is correctly formatted by dropping the first row if it contains column names
if mapping.iloc[0,0]=='artist_id':
    mapping=mapping.drop([0])
else:
    print('no need to drop first row')

# Calculate a 'score' column for ranking tracks based on list position
chart['score']=score(chart['list_position']).astype('int')
chart['chart_year']=pd.to_datetime(chart['chart_week']).dt.year

# Merge datasets to create a comprehensive dataset
map_artist=merge_artist(mapping,artist)
artist_track=merge_track(map_artist,tracks)
data=merge_track(artist_track,chart)
print('finished data import')

# Create artist-based summary dataset
data_artist = data.copy()
data_year=merge_artist(data_artist.groupby('artist_id')['score'].sum(),artist)
data_year=merge_artist(data_year,data_artist.groupby('artist_id')['name_y'].nunique())
data_year=merge_artist(data_year,data_artist.groupby('artist_id')['chart_week'].count())
data_year=merge_artist(data_year,data_artist[data_artist['list_position']==1][['artist_id','score']].groupby('artist_id').count())
data_year=data_year.sort_values(by='score_x',ascending=False).reset_index()

# Identify artists that might need correction based on popularity and score thresholds
artist_to_clean=data_year[(data_year['score_x'] > 200+pow(10,(0.041*(data_year['popularity']+40))))]
artist_to_clean=artist_to_clean[artist_to_clean['followers']<=25000]

# Extract list of songs by artists that need correction
list_of_songs=data[data['artist_id'].isin(artist_to_clean['artist_id'])]['name_y'].unique()

print('finished setting up songs to find new artist to')

# Preprocess song names to remove extra characters for better search accuracy
df_songs=pd.DataFrame(list_of_songs)
df_songs=df_songs.rename(columns={df_songs.columns[0]:'first'})
df_songs["-(_column"]=df_songs['first'].str.split('(').str[0]
df_songs["--_column"]=df_songs['-(_column'].str.split('-').str[0]

print('start importing from musicbrainz')

# Query MusicBrainz API to find correct artist information
list_to_correct=df_songs['--_column'].to_list()
artist_correct=pd.DataFrame(columns=['query','id','title','artist','num'])
n=0
errors=0
print(f"estimated time= {len(list_to_correct)*2} sek")
while n<len(list_to_correct):
    url=f"""https://musicbrainz.org/ws/2/release/?query=release:"{list_to_correct[n]}"&fmt=json"""
    response = requests.get(url)
    data_resp=response.json()
    if response.status_code==200:
        t=0
        while t<len(data_resp['releases']):
            i=0
            list=[list_to_correct[n],
                data_resp['releases'][t]['id'],
                data_resp['releases'][t]['title']]
            while  i<len(data_resp['releases'][t]['artist-credit']):
                list2=list.copy()
                list2.append(data_resp['releases'][t]['artist-credit'][i]['name'])
                list2.append(i)
                artist_correct.loc[len(artist_correct)] = list2
                i=i+1
            t=t+1
        n=n+1
    else:
        time.sleep(2) #sleeping a bit to prevent API limit per second error
        print(errors)
        errors=errors+1
    time.sleep(1.3) #sleeping a bit to prevent API limit per second error

print('finished importing from musicbrainz')

# Determine whether the artist already exists in the dataset
artist_correct['existing_artist']=artist_correct['artist'].isin(artist['name'])
artist_correct=pd.merge(artist_correct, artist_correct.groupby(['query','artist']).count()['num'],on=['query','artist'])
artist_correct=pd.merge(artist_correct,artist_correct.groupby(['id'])['existing_artist'].sum(),on='id')
artist_correct=pd.merge(artist_correct,artist_correct.groupby('id')[['num_y','existing_artist_y']].mean().sum(axis=1).reset_index(),on='id')

# Identify and correct artist names using Levenshtein distance
df_corrected_song=artist_correct[artist_correct['id'].isin(artist_correct.loc[artist_correct.groupby('query').idxmax()[0]]['id'])]
df_songs_with_track_id=pd.merge(df_songs,data[data['name_y'].isin(df_songs['first'])&data['name_x'].isin(artist_to_clean['name'])][['name_y','track_id']],left_on='first',right_on='name_y',how='left').drop_duplicates()
df_songs_with_track_id=pd.merge(df_songs_with_track_id,df_corrected_song[['id','query']],left_on='--_column',right_on='query',how='left').drop_duplicates()
artist_to_compare=pd.DataFrame(columns=['artist','name','popularity','dist'])
clone_artist=artist.copy()

list_to_find_artist=df_corrected_song[~df_corrected_song['existing_artist_x']]['artist'].to_list()
for item in list_to_find_artist:
    listy=item.lower()
    i=0
    for items in clone_artist['name']:
        items=items.lower()
        dist=Levenshtein.distance(items,listy)
        clone_artist.loc[i,'dist']=dist
        i=i+1
    artist_to_compare= pd.concat([artist_to_compare, pd.DataFrame([{'artist':item, **clone_artist.sort_values(by='dist').iloc[0][['name','popularity','dist']].to_dict()}])])

print('finished levensthein distance')

# Update mapping with corrected artist names
artist_to_change=artist_to_compare[artist_to_compare['dist']<=1].drop_duplicates()
df_corrected_song['artist']=df_corrected_song['artist'].replace(artist_to_change.set_index('artist')['name'].to_dict())
df_corrected_song=pd.merge(df_corrected_song,artist[['artist_id','name']],left_on='artist',right_on='name',how='left')
df_corrected_song=pd.merge(df_corrected_song,df_songs_with_track_id[['id','track_id']],on='id')
mapping= mapping[~mapping['track_id'].isin(df_corrected_song['track_id'])]
updated_mapping=pd.concat([mapping,df_corrected_song[['artist_id','track_id']].dropna()])

updated_mapping.to_csv('updated_mapping.csv',index=False)
print('finished')






