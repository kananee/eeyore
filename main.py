from tweepy import OAuthHandler
from tweepy import API
import tweepy
import pandas as pd
from datetime import tzinfo
from datetime import datetime,timedelta
import datetime as dt
import time
import json
from os import environ
import requests

access_token=environ['access_token']
access_token_secret=environ['access_token_secret']
consumer_key=environ['consumer_key']
consumer_secret=environ['consumer_secret']
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = API(auth)
token = environ['token']

class FixedOffset(tzinfo):
    def __init__(self, offset):
        self.__offset = timedelta(hours=offset)
        self.__dst = timedelta(hours=offset-1)
        self.__name = ''

    def utcoffset(self, dt):
        return self.__offset

    def tzname(self, dt):
        return self.__name

    def dst(self, dt):
        return self.__dst

def notify(msg):
  url = 'https://notify-api.line.me/api/notify'
  headers = {'content-type':'application/x-www-form-urlencoded','Authorization':'Bearer '+token}
  r = requests.post(url, headers=headers , data = {'message':msg})

def DateTimeNow():
  date_now=datetime.strftime(datetime.now(FixedOffset(7)),"%Y/%m/%d")
  Time_now=datetime.strftime(datetime.now(FixedOffset(7)),"%H:%M:%S")
  return(date_now,Time_now)

def DateTimePrv():
  date_prv=datetime.strftime(datetime.now(FixedOffset(7))-timedelta(1),"%Y/%m/%d")
  Time_prv='00:00:00'
  return(date_prv,Time_prv)

def Timeloop():
  Timeupdate=dt.datetime.now(FixedOffset(7))
  return(Timeupdate)

def Futuretime():
  Time_Future=datetime.strftime(datetime.now(FixedOffset(8)),"%H:00:00")
  return(Time_Future)

def Today_Data():
  Time_Data=datetime.strftime(datetime.now(FixedOffset(7))-timedelta(1),"%Y-%m-%d")
  return(Time_Data)

def Tweet_Announcement():
  Ann_text='📢 Reply Hashtag to this tweet for more detail data\n[ the most hastag will tweet detail at '+str(Futuretime())+' ]'
  Tweets=Ann_text
  return(Tweets)

def Proess_CalTag(tweet_id):
  #Timeline=api.user_timeline(user_id='432538747',count=1,page=1,exclude_replies=True)
  #tweet_id=Timeline[0].id_str

  Data=[]
  username='BearguinTrend'
  for tweet in tweepy.Cursor(api.search,q='to:{}'.format(username),count=1000,since_id=tweet_id, tweet_mode='extended').items(1000):
    Data.append({'ids':tweet.user.id, 'Text':tweet.full_text,'Has':tweet.entities.get('hashtags')})

  df=pd.DataFrame(Data)
  df=df.drop_duplicates(subset=['ids'])

  hastag=[]
  for i in df['Has']:
      rm_has=[]
      for items in i:
        rm_has.append(items['text'].lower())
      rm_has=list(dict.fromkeys(rm_has))
      for j in rm_has:
        hastag.append(j)

  df_hastag=pd.DataFrame({'#Hastag':hastag})
  df_hastag['Count']=1
  df_hastag=df_hastag.groupby(['#Hastag']).sum()
  All_Has=df_hastag.sum()[0]
  df_hastag=df_hastag.sort_values(by=['Count'], ascending=False)

  S_HAS=df_hastag.reset_index()['#Hastag'][0]
  S_VALUE=df_hastag.reset_index()['Count'][0]

  return(S_HAS,S_VALUE,All_Has)

def Reply_Summary(tweet_id):
  #Timeline=api.user_timeline(user_id='432538747',count=1,page=1,exclude_replies=True)
  #tweet_id=Timeline[0].id_str
  try:
    Check=0
    S_HAS,S_VALUE,All_Has=Proess_CalTag(tweet_id)
    api.update_status(status = 'Hashtag voting results '+str(DateTimeNow()[0])+' '+str(DateTimeNow()[1])+'\n\n#'+str(S_HAS)+' '+str(round(S_VALUE/All_Has*100,2))+' %', in_reply_to_status_id = tweet_id , auto_populate_reply_metadata=True)
    S_HAS='#'+str(S_HAS)
  except:
    Check=1
    S_HAS=Name
  return(Check,S_HAS)

def Ads():
  if(Timeloop().minute<30):
    Ads_post1=Ads_Slot1[(Ads_Slot1['Time']==Timeloop().hour) & (Ads_Slot1['Part']==1)]['text'].iloc[0]
    Ads_post2=Ads_Slot2[(Ads_Slot2['Time']==Timeloop().hour) & (Ads_Slot2['Part']==1)]['text'].iloc[0]
  else:
    Ads_post1=Ads_Slot1[(Ads_Slot1['Time']==Timeloop().hour) & (Ads_Slot1['Part']==2)]['text'].iloc[0]
    Ads_post2=Ads_Slot2[(Ads_Slot2['Time']==Timeloop().hour) & (Ads_Slot2['Part']==2)]['text'].iloc[0]
  return(Ads_post1,Ads_post2)

def Ads_update():
  file_name = 'https://docs.google.com/spreadsheet/ccc?key=1RxB3Oa3QyfcMz15-WhHFlsWVJiDc-c6umNQHDpvYEIQ&output=xlsx'
  Ads_Slot1 = pd.read_excel(file_name,sheet_name='Slot2')
  Ads_Slot2 = pd.read_excel(file_name,sheet_name='Slot1')
  return(Ads_Slot1,Ads_Slot2)

def TopTrends():
  Twitter_trend=api.trends_place(1225448)
  Trends = json.loads(json.dumps(Twitter_trend, indent=1))
  Name_Trend=[]
  Tweet_Volumn=[]
  for i in Trends[0]["trends"]:
    if 'Noneee' not in i["name"]:
        Name_Trend.append(i["name"]) 
        Tweet_Volumn.append(i["tweet_volume"])



  Tweet_Text=str(DateTimeNow()[0])+' '+str(DateTimeNow()[1])+'\n'
  for i in range(0,5):
    Tweet_Text=Tweet_Text+str(i+1)+'. '+str(Name_Trend[i])+'\n'
  Tweet_Text=Tweet_Text+'\n'+str(Ads()[0])
  api.update_status(status = Tweet_Text)
  time.sleep(20)



  Tweet_Text=str(DateTimeNow()[0])+' '+str(DateTimeNow()[1])+'\n'
  for i in range(5,10):
    Tweet_Text=Tweet_Text+str(i+1)+'. '+str(Name_Trend[i])+'\n'
  if(Timeloop().minute<30):
      Tweet_Text=Tweet_Text+'\n'+Tweet_Announcement()
  else:
      Tweet_Text=Tweet_Text+'\n'+str(Ads()[1])
  api.update_status(status = Tweet_Text)

  for i in Name_Trend:
    if i not in List_has:
      Name=i
      List_has.append(i)
      break

  Timeline=api.user_timeline(user_id='1252056460608933888',count=1,page=1,exclude_replies=True)
  tweet_id=Timeline[0].id_str

  return(tweet_id,Name)

def search_tweet(Name):
  lang=''
  Retweets=" -filter:retweets"
  Data=list()
  try:
    for tweet in tweepy.Cursor(api.search,q=str(Name)+Retweets,count=1000,since=Today_Data(),lang=lang).items():
      Data.append({'Retweet':tweet.retweet_count,'Favorite':tweet.favorite_count,'Has':tweet.entities.get('hashtags'),'ids':tweet.user.id,'join_date':tweet.user.created_at})
  except tweepy.TweepError:
    time.sleep(10)
  
  df=pd.DataFrame(Data)
  df['today']=pd.Timestamp.today()
  df['age']=df['today']-df['join_date']
  df['dif_age']=df['age'].dt.days
  df['dif_age']=df['dif_age']/365

  return(df)

def related_hashtag(df):
    hastag=[]
    for i in df['Has']:
        for items in i:
            hastag.append(items['text'].lower())
        df_hastag=pd.DataFrame({'#Hastag':hastag})
        df_hastag['Count']=1
        df_hastag=df_hastag.groupby(['#Hastag']).sum()
        df_hastag=df_hastag.sort_values(by=['Count'], ascending=False)
    df_hastag=df_hastag.head(6)
    df_hastag=df_hastag.tail(5)
    df_hastag=df_hastag.reset_index()

    Text_Hash=[]
    for i in range(0,len(df_hastag)):
        Text_Hash.append(df_hastag['#Hastag'][i])
    return(Text_Hash)

def Tweet_Data(df,Text_Hash):
  if(len(df)>16500):
    Tweets='>'+str(len(df))
    Users='>'+str(df[['ids']].drop_duplicates().count()[0])
  else:
    Tweets=str(len(df))
    Users=str(df[['ids']].drop_duplicates().count()[0])
  Text_tweet='Data on '+str(Name)+' '+str(Today_Data())+'\n'
  Text_tweet=Text_tweet+'Tweets : '+Tweets+'\nUsers : '+Users+'\nRetweets : '+str(df['Retweet'].sum(axis = 0, skipna = True))+'\nLikes : '+str(df['Favorite'].sum(axis = 0, skipna = True))+'\nTop 5 Related #\n'
  for i in range(0,5):
    Text_tweet=Text_tweet+str(i+1)+'. '+str(Text_Hash[i])+'\n'
  api.update_status(status = Text_tweet)

List_has=[]
Ads_Slot1,Ads_Slot2=Ads_update()
notify('Twitter BearGuinTrend Start!!! 🦄')
while True:
  Minute=Timeloop().minute
  Hour=Timeloop().hour
  if(Minute==15):
    tweet_id,Name=TopTrends()
    time.sleep(20)

  if(Minute==30):
    df=search_tweet(Name)
    Text_Hash=related_hashtag(df)
    Tweet_Data(df,Text_Hash)
    time.sleep(20)

  if(Minute==45):
    tweet_id2,Name=TopTrends()
    time.sleep(20)

  if(Minute==59):
    Post,Name=Reply_Summary(tweet_id)
    time.sleep(60)
    df=search_tweet(Name)
    Text_Hash=related_hashtag(df)
    Tweet_Data(df,Text_Hash)

  if(Hour==23 and Minute==50):
    Ads_Slot1,Ads_Slot2=Ads_update()
    notify('Reset Ads 🎈')


  time.sleep(40)



















