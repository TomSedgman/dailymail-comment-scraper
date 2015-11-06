#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    # For Python 3.0 and later
    from urllib.request import urlopen
    from urllib import HTTPError, URLError
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen, HTTPError, URLError
import json, base64, re
import xmltodict
from random import randint

# Function to get json data from a url 
def get_jsonparsed_data(url):

    try:
       response = urlopen(url)
    except HTTPError, err:
       if err.code == 404:
           return "Page not found!"
       elif err.code == 403:
           return "Access denied!"
       else:
           return "Something happened! Error code", err.code
    except URLError, err:
        return "Some other error happened:", err.reason

    data = str(response.read())
    return json.loads(data);

# Function to get xml data as json from a url: 

def get_xml_as_json(request):
    file = urlopen(request)
    data = file.read()
    file.close()

    data = xmltodict.parse(data)
    return json.dumps(data)


urlArticleList = "http://www.dailymail.co.uk/home/index.rss"
# done = 0
# maxTries = 10

# while done < maxTries:

# Get the 'hottest' stories for comments
jsonDataStories = get_xml_as_json(urlArticleList)

#print jsonDataStories 

#Pick random story
# try:
storiesNumber = len(jsonDataStories["rss"]["channel"]["item"])
#         storiesNorm = randint(0,(storiesNumber - 1))
print storiesNumber

#     except:
#         done +=1
#         continue

#     try:

#         # Read the 'Hottest' story title and ID
#         articleTitle = jsonDataStories["data"][storiesNorm]["title"]
#         articleID =  str(jsonDataStories["data"][storiesNorm]["articleId"])
#         # Encode ID using Base 64
#         articleIDBase64 = base64.b64encode(articleID)

#     except:
#         done +=1
#         continue

#     # Build URL for the top comments on the article 
#     urlTopLikes = "http://bskyb.bootstrap.fyre.co/api/v3.0/site/360818/article/"+articleIDBase64+"/top/likes/"

#     # Get top comments
#     try: 
#         jsonDataComments = get_jsonparsed_data(urlTopLikes)
        
#     except: 
#         done +=1
#         continue

#     # Pick a random comment

#     try:
#         ratedComments = len(jsonDataComments["data"]["content"])
#         ratedCommentNorm = randint(0,(ratedComments - 1))
#     except: 
#         done +=1
#         continue
    
#     #Read Horrible Comment and number of likes
#     try: 

#         horribleCommentHTML = jsonDataComments["data"]["content"][ratedCommentNorm]["content"]["bodyHtml"]
#         numberOfLikes = jsonDataComments["data"]["content"][ratedCommentNorm]["content"]["annotations"]["likes"]
    
#     except: 
#         done +=1
#         continue

#     #Strip out html tags
#     def cleanhtml(raw_html):

#         cleanr =re.compile('<.*?>')
#         cleantext = re.sub(cleanr,'', raw_html)
#         return cleantext;

#     filth = cleanhtml(horribleCommentHTML)

#     break

# if done == maxTries:
#     errorString = "Sorry, LiveFyre's API is being about as good as Vigiglobe's"
#     return {"comment": errorString}


# else:
#     # Return the horrible comment
#     return {"comment": filth, "storyTitle": articleTitle, "numberOfLikes": numberOfLikes}