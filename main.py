import tweepy
from tweepy import OAuthHandler
from tweepy import API
import datetime as dt
import  time
from os import environ
import json
from datetime import datetime,timedelta
import pandas as pd
import requests
from datetime import tzinfo

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
    
url = 'https://notify-api.line.me/api/notify'
token = environ['token']
headers = {'content-type':'application/x-www-form-urlencoded','Authorization':'Bearer '+token}
msg ='Program runnning Top Trends Thailand'
r = requests.post(url, headers=headers , data = {'message':msg})

file_name = 'https://docs.google.com/spreadsheet/ccc?key=1RxB3Oa3QyfcMz15-WhHFlsWVJiDc-c6umNQHDpvYEIQ&output=xlsx'
df_slot2 = pd.read_excel(file_name,sheet_name='Slot2')
df_slot1 = pd.read_excel(file_name,sheet_name='Slot1')

d_slot1=df_slot1.to_dict('split')
d_slot2=df_slot2.to_dict('split')

access_token=environ['access_token']
access_token_secret=environ['access_token_secret']
consumer_key=environ['consumer_key']
consumer_secret=environ['consumer_secret']
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = API(auth)


def trend_twitter():  #ดึงข้อมูล Trends Twitter
    brazil_trends=api.trends_place(1225448)
    trends = json.loads(json.dumps(brazil_trends, indent=1))
    
    Name_trend=[]
    tweet_volume=[]
    for i in trends[0]["trends"]:
        if 'asdfg' not in i["name"]:
            Name_trend.append(i["name"]) 
            tweet_volume.append(i["tweet_volume"])    
           
    return(Name_trend,tweet_volume)

def top10(trend_text,A,B,ad): #top n value 
    trend_plot=[]

    text='Top Trends Thailand '+Time
    for i in range(A,B):
        text=text+'\n'+str(i+1)+') '+trend_text[i]
        trend_plot.append(trend_text[i])
    text=text+"\n\n"+str(ad)
    return(text)


def twitter_data(Name,lang,Retweets):
    now = datetime.strftime(datetime.now()-timedelta(1),"%Y-%m-%d")
    now1 = datetime.strftime(datetime.now(),"%Y-%m-%d")
    #now=now.strftime("%Y-%m-%d")
    Data=list()
    try:
        for tweet in tweepy.Cursor(api.search,q=str(Name)+Retweets,count=1000,since=now,lang=lang).items():
            Data.append({'created_at':tweet.created_at,
                          'texts':tweet.text,
                     'id':tweet.id,
                     'source':tweet.source,
                     'geo':tweet.geo,
                     'lang':tweet.lang,
                      'Retweet':tweet.retweet_count,
                      'Favorite':tweet.favorite_count,
                      'id_str':tweet.id_str,
                      'place':tweet.place,
                      'entities':tweet.entities,
                      'Has':tweet.entities.get('hashtags'),
                      'followers_count':tweet.user.followers_count,
                      'protected':tweet.user.protected,
                      'description':tweet.user.description,
                      'name':tweet.user.screen_name,
                      'friends_count':tweet.user.friends_count,
                      'statuses_count':tweet.user.statuses_count,
                      'ids':tweet.user.id,
                      'location':tweet.user.location,
                      'profile_image_url':tweet.user.profile_image_url,
                      'join_date':tweet.user.created_at
                      
                 })
            #time.sleep(0.055)
        
    except tweepy.TweepError:
        time.sleep(10) # sleep for 2 minutes. You may try different time
        #print('Maximum')
    df=pd.DataFrame(Data)
    df=df.set_index('created_at')
    df=df.tz_localize('Etc/GMT+7', level=0).tz_convert(None)
    df=df.reset_index()
    #print(df)
    df['today']=pd.Timestamp.today()
    df['age']=df['today']-df['join_date']
    df['dif_age']=df['age'].dt.days
    df['dif_age']=df['dif_age']/365
    df[df['created_at']==now1]
    #print('dfcom')
    return(df,now)

def related_hashtag(df,text_has):
    hastag=[]
    #pd.DataFrame(k['fgfdgd'])
    for i in df['Has']:
        for items in i:
            hastag.append(items['text'].lower())
            #print(t['text'])

        
        df_hastag=pd.DataFrame({'#Hastag':hastag})
        df_hastag['Count']=1
        df_hastag=df_hastag.groupby(['#Hastag']).sum()
        df_hastag=df_hastag.sort_values(by=['Count'], ascending=False)
    df_hastag=df_hastag.head(6)
    df_hastag=df_hastag.tail(5)
    df_hastag=df_hastag.reset_index()
    #print(len(df_hastag))
    
    for i in range(0,len(df_hastag)):
        #print(df_hastag['#Hastag'][i])
        text_has=text_has+'\n'+str(i+1)+') '+'#'+str(df_hastag['#Hastag'][i])
    return(text_has)




listhas=[]
diffollow=0 

while True:
    Timeupdate=dt.datetime.now(FixedOffset(7))
    if(Timeupdate.minute==15 or Timeupdate.minute==45):
        Time=str(Timeupdate.strftime("%x"))+'  '+str(Timeupdate.strftime("%X"))
        if(Timeupdate.minute==15):
            timecheck=1
        elif(Timeupdate.minute==45):
            timecheck=2
        for i in d_slot1['data']:
            if(i[0]==Timeupdate.hour and i[1]==timecheck):
                Tweets_slot1=i[5]
        for i in d_slot2['data']:
            if(i[0]==Timeupdate.hour and i[1]==timecheck):
                Tweets_slot2=i[5]
        
        trend_text=trend_twitter()
        text1=top10(trend_text[0],0,5,Tweets_slot2)
        try:
            api.update_status(status=text1)
        except:
            text1=text1[30:]
            api.update_status(status=text1)
        text2=top10(trend_text[0],5,10,Tweets_slot1)
        time.sleep(40)
        try:
            api.update_status(status=text2)
        except:
            text2=text2[30:]
            api.update_status(status=text2)
        
        for i in trend_text[0]:
            if i not in listhas:
                hashtag=i
                listhas.append(i)
                break
                
        #Retweets=" -filter:retweets"   #  " -filter:retweets"  ไม่รวม Retweet  , ""  รวม Retweet
        #lang='' #'th' , 'en' , 'jp'  เว้นว่างสำหรับทุกภาษา 
        #df,now=twitter_data(hashtag,lang,Retweets) 
        #text_has='Data on '+hashtag+'   '+str(now)+'\nTweets   :  '+str(len(df))+'\nUSERS  :  '+str(df[['ids']].drop_duplicates().count()[0])+'\nRetweets  :  '+str(df['Retweet'].sum(axis = 0, skipna = True))+'\nLikes  :  '+str(df['Favorite'].sum(axis = 0, skipna = True))+'\nTop 5 Related #'
        #df_has=related_hashtag(df,text_has)
        time.sleep(60)
                
    #if(Timeupdate.minute==0 or Timeupdate.minute==30):
        #try:
            #api.update_status(status=df_has)
            #time.sleep(60)
            #if(len(listhas)>10):
                #listhas.pop(0)
                #if(len(listhas)>10):
                    #listhas.pop(0)
        #except:
            #time.sleep(60)
            
    if(Timeupdate.hour==0 and Timeupdate.minute==3):
        try:
            file_name = 'https://docs.google.com/spreadsheet/ccc?key=1RxB3Oa3QyfcMz15-WhHFlsWVJiDc-c6umNQHDpvYEIQ&output=xlsx'
            df_slot2 = pd.read_excel(file_name,sheet_name='Slot2')
            df_slot1 = pd.read_excel(file_name,sheet_name='Slot1')

            d_slot1=df_slot1.to_dict('split')
            d_slot2=df_slot2.to_dict('split')
            
            
            url = 'https://notify-api.line.me/api/notify'
            token = environ['token']
            headers = {'content-type':'application/x-www-form-urlencoded','Authorization':'Bearer '+token}
            msg ='Reset Ads BearGuin'
            r = requests.post(url, headers=headers , data = {'message':msg})
            time.sleep(60)
            
        except:
            time.sleep(60)
    if(Timeupdate.hour==23 and Timeupdate.minute==55):
        Data=list()  
        try:
            for i in range(1,25):
                for tweet in api.user_timeline(id="BearguinTrend",page=i):
                    Data.append({'created_at':tweet.created_at,
                        'texts':tweet.text,
                        'id':tweet.id,
                        'source':tweet.source,
                        'geo':tweet.geo,
                        'lang':tweet.lang,
                        'Retweet':tweet.retweet_count,
                        'Favorite':tweet.favorite_count,
                        'id_str':tweet.id_str,
                        'place':tweet.place,
                        'entities':tweet.entities,
                        'Has':tweet.entities.get('hashtags'),
                        'followers_count':tweet.user.followers_count,
                        'protected':tweet.user.protected,
                        'description':tweet.user.description,
                        'name':tweet.user.screen_name,
                        'friends_count':tweet.user.friends_count,
                        'statuses_count':tweet.user.statuses_count,
                        'ids':tweet.user.id,
                        'location':tweet.user.location,
                        'profile_image_url':tweet.user.profile_image_url,
                        'join_date':tweet.user.created_at
                    })



        except tweepy.TweepError:
            time.sleep(20) # sleep for 2 minutes. You may try different time
        df=pd.DataFrame(Data)
        df=df.set_index('created_at')
        df=df.tz_localize('Etc/GMT+7', level=0).tz_convert(None)
        df=df.reset_index()                
        today = Timeupdate
        df['year'] = pd.DatetimeIndex(df['created_at']).year
        df['month'] = pd.DatetimeIndex(df['created_at']).month
        df['day'] = pd.DatetimeIndex(df['created_at']).day
        df['hour'] = pd.DatetimeIndex(df['created_at']).hour
        df['min'] = pd.DatetimeIndex(df['created_at']).minute        
        
        df=df[(df.day == Timeupdate.day) & (df.month == Timeupdate.month)]
        df.loc[ (df['min'] <= 17) & (df['min'] >= 14 ), 'Type'] = 'A'
        df.loc[ (df['min'] <= 47) & (df['min'] >= 44 ), 'Type'] = 'B'
        df['Type']=df['hour'].astype(str)+df['Type']
        
        list_time=['0A','0B','1A','1B','2A','2B','3A','3B','4A','4B','5A','5B','6A','6B','7A','7B','8A','8B','9A','9B','10A','10B','11A','11B','12A','12B','13A','13B','14A','14B','15A','15B','16A','16B','17A','17B','18A','18B','19A','19B','20A','20B','21A','21B','22A','22B','23A','23B']       

        Table=pd.DataFrame(list_time)
        Table=Table[~Table[0].isin(df['Type'])]
        
        text='\nError slot BearGuin   '+today.strftime("%Y-%m-%d")

        for i in Table[0]:
            text=text+'\nSlot   '+i        
        url = 'https://notify-api.line.me/api/notify'
        token = environ['token']
        headers = {'content-type':'application/x-www-form-urlencoded','Authorization':'Bearer '+token}
        
        df=df.drop(columns=['year','month','day','hour','min','Type'])
        msg =text+'\n\n Retweets :  '+str(df['Retweet'].sum())+'\n Likes :  '+str(df['Favorite'].sum())+'\n Followers :  '+str(round(df['followers_count'].mean(),0)-diffollow)+' Change: '+str(df['followers_count'].mean())
        diffollow=df['followers_count'].mean()
        r = requests.post(url, headers=headers , data = {'message':msg})
        time.sleep(40)
        
    time.sleep(40)
