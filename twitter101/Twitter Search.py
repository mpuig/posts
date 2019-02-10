#!/usr/bin/env python
# coding: utf-8

# # Twitter Search
# 
# A lot of NLP projects use Twitter as data source. Here we'll see some ways to obtain Tweets for use in your applications. One way to start testing searches for Tweets, is to first use the twitter.com/search UI, and build an API version from its guidance. There is absolutely not complete parity or completeness, but it's enough to get started. 
# 
# We want to search for Tweets referencing Barcelona. First, we run the search on twitter.com/search
# 
# https://twitter.com/search?q=barcelona
# 
# Once we have the desired query, there are several tools to obtain Tweets programmatically. The ways explained in this post are based on Python, and some of them are based on the official Twitter RESTful API, and some of them not.
# 
# The easiest (ans safest) one is the Twitter API. The Twitter API platform offers three tiers of search APIs, but here we'll focus on two of them. The first one is the Twitter Standard which is free and with the restriction that searches against a sampling of recent Tweets published in the past 7 days. To overcome these limits, Twitter offers a Premium API, which has free and paid access to either the last 30 days of Tweets or access to Tweets from as early as 2006. [Twitter Search explanation](https://developer.twitter.com/en/docs/tweets/search/overview).
# 
# 

# In[1]:


import json
from pathlib import Path, PurePath

TWITTER_QUERY = "barcelona"
DATA_DIR = Path.cwd() / "data"

Path(DATA_DIR).mkdir(parents=True, exist_ok=True)


# ## Twitter search with Standard API
# 
# [Twitter Standard API documentation](https://developer.twitter.com/en/docs/tweets/search/overview/standard)
# 
# ### Using Python 
# 
# First step is Oauth2 authentication. To start, a new app must be created (here](https://developer.twitter.com/app/new). Then click on the 'Keys and Access Tokens' page and retrieve the Consumer Key and Consumer Secret. Open the file `secrets.py.example`, save a copy as `secrets.py`, and finally fill the values.

# In[2]:


from secrets import APP_KEY, APP_SECRET


# Next step is to obtain a Bearer Token. To do this, make a `POST` request to the authentication endpoint, and the returned value will be included in subsequent API requests.

# In[15]:


import requests
import base64

key_secret = f'{APP_KEY}:{APP_SECRET}'.encode('ascii')
b64_encoded_key = base64.b64encode(key_secret)
b64_encoded_key = b64_encoded_key.decode('ascii')

base_url = 'https://api.twitter.com/'
auth_url = f'{base_url}oauth2/token'

auth_headers = {
    'Authorization': f'Basic {b64_encoded_key}',
    'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
}

auth_data = {
    'grant_type': 'client_credentials'
}

auth_resp = requests.post(auth_url, headers=auth_headers, data=auth_data)

# Check status code okay
assert auth_resp.status_code==200

# Keys in data response are token_type (bearer) and access_token (your access token)
access_token = auth_resp.json()['access_token']
print(access_token)


# Twitter documentation has extense information about the API use. The reference to make queries can be found at https://developer.twitter.com/en/docs/api-reference-index. 
# 
# Different options for search parameters can be found at https://developer.twitter.com/en/docs/tweets/search/api-reference/get-search-tweets.html

# In[16]:


search_headers = {
    'Authorization': f'Bearer {access_token}'
}

search_params = {
    'q': TWITTER_QUERY,
    'result_type': 'recent',
    'count': 5
}

search_url = f'{base_url}1.1/search/tweets.json'
search_resp = requests.get(search_url, headers=search_headers, params=search_params)
assert search_resp.status_code==200

# There is a lot of information that comes with this data, 
# including search metadata, geolocations, twitter author information etc. 
# Here only use the 'statuses' objects.
tweets = search_resp.json()

# Print the tweet text
for tweet in tweets['statuses']:
    print(tweet['text'] + '\n')


# ### Using a Python library
# 
# Another way to use the Twitter API is with third party libraries. In this case we use [Twython](https://twython.readthedocs.io/en/latest/), a pure Python wrapper that supports both normal and streaming Twitter APIs. Those libraries tend to simplify the access to the API.

# In[18]:


from twython import Twython

twitter = Twython(APP_KEY, APP_SECRET, oauth_version=2)
ACCESS_TOKEN = twitter.obtain_access_token()
twitter = Twython(APP_KEY, access_token=ACCESS_TOKEN)
    
tweets = twitter.search(q=TWITTER_QUERY)

# In this case, save the tweets in different json files
for tweet in tweets['statuses']:
    filename = DATA_DIR / (tweet['id_str'] + '.json')
    with open(filename, 'w') as fp:
        json.dump(tweet, fp, indent=2)


# ## Twitter search with Premium API
# 
# If 7 days back is not enough, for a given project, then it's necessary use the 
# [Twitter Premium API](https://developer.twitter.com/en/docs/tweets/search/overview/premium). This API gives the possibility to go back until 2006, or to use [premium operators](https://developer.twitter.com/en/docs/tweets/search/guides/premium-operators) not available with the Standard API.
#     
# [SearchTweets](https://github.com/twitterdev/search-tweets-python), a Python wrapper for Twitter Premium and Enterprise Search APIs

# In[4]:


from searchtweets import gen_rule_payload, load_credentials, collect_results

premium_search_args = load_credentials("./twitter_keys.yml",
                                       yaml_key="search_tweets_premium",
                                       env_overwrite=False)

rule = gen_rule_payload(TWITTER_QUERY, from_date="2019-02-01", results_per_call=500)
tweets = collect_results(rule, max_results=500, result_stream_args=premium_search_args)
filename = DATA_DIR / 'tweets_premium.json'
with open(filename, 'w') as fp:
    json.dump(tweets, fp, indent=2)


# ## Twitter scrapers
# 
# An alternative to the Twitter APIs to download Tweets is scraping the Twitter site directly. There are some useful tools like allowing to scrape a user's followers, following, Tweets and more while evading most API limitations. here we'll use [Twint](https://github.com/twintproject/twint) a Twitter scraping tool written in Python. Twint scraper is based on the Beautifulsoup library to parse the Twitter pages. 
# 
# In this example, we'll execute the same query, and results will be saved in a csv file into the `data` directory.

# In[4]:


import twint

c = twint.Config()
c.Search = TWITTER_QUERY
c.Store_csv = True
c.Output = "data"
c.Since = "2019-01-01"
c.Limit = 100
c.Hide_output = True
twint.run.Search(c)


# For more advanced python users, an alternative is to write your own scraper using [chromedriver](https://sites.google.com/a/chromium.org/chromedriver/), and Selenium to open up a browser and visit Twitter's search page. A nice example can be found on this [tutorial from Data4Democracy](https://github.com/Data4Democracy/tutorials/blob/master/Twitter/Twitter_Gettingpast_32K_Limit.ipynb)

# In[ ]:




