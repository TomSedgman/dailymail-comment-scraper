#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from os import environ as env
from sys import argv

import bottle
from bottle import default_app, request, route, response, get

bottle.debug(True)

@get('/')
def index():
  response.content_type = 'text/json; charset=utf-8'
  try:
      # For Python 3.0 and later
      from urllib.request import urlopen
      from urllib import HTTPError, URLError
  except ImportError:
      # Fall back to Python 2's urllib2
      from urllib2 import urlopen, HTTPError, URLError
  import base64, re, lxml, xmltodict
  from lxml import objectify
  import simplejson as json
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
  def get_xml(request):
      file = urlopen(request)
      data = file.read()
      file.close()

      xmlData = xmltodict.parse(data)
      return xmlData

  # URL for Daily Mail's RSS feed:
  urlArticleList = "http://www.dailymail.co.uk/home/index.rss"

  # How many times to retry
  done = 0
  maxTries = 50000

  while done < maxTries:

    # Get all stories from the rss feed
    try:

      xmlDataStories = get_xml(urlArticleList)
      jsonDataStories = json.dumps(xmlDataStories)
      jsonDataStoriesLoaded = json.loads(jsonDataStories)

    except:
      done +=1
      continue


    # Pick random story
    try:
      storiesNumber = len(jsonDataStoriesLoaded["rss"]["channel"]["item"])
      storyNumber = randint(0,(storiesNumber - 1))

    except:
      done +=1
      continue

    # Get the Stpry ID and clean up the URL
    try:  
      storyURL = jsonDataStoriesLoaded["rss"]["channel"]["item"][storyNumber]["link"]
      shortStoryURL = storyURL.split('?', 1)[0]
      storyIDAlmost = shortStoryURL.split('-', 1)[-1] 
      storyID = storyIDAlmost.split('/', 1)[0]

    except:
      done +=1
      continue

    # Maximum Number of comments we want to get from the API
    maxCommentNumber = str(20)

    # Build the URL to return the 'Best Rated' comments for the random story
    urlForComments = "http://www.dailymail.co.uk/reader-comments/p/asset/readcomments/"+storyID+"?max="+maxCommentNumber+"&sort=voteRating&order=desc&rcCache=shout"

    # Get comment and metadata
    try:
      jsonDataComments = get_jsonparsed_data(urlForComments)
      commentsNumber = len(jsonDataComments["payload"]["page"])
      randomCommentNumber = randint(0,(commentsNumber - 1))
      commentBody = jsonDataComments["payload"]["page"][randomCommentNumber]["message"]
      userName = jsonDataComments["payload"]["page"][randomCommentNumber]["userAlias"]
      downVotes = int((jsonDataComments["payload"]["page"][randomCommentNumber]["voteCount"] - jsonDataComments["payload"]["page"][randomCommentNumber]["voteRating"]) * 0.5)
      upVotes = int(jsonDataComments["payload"]["page"][randomCommentNumber]["voteRating"] + downVotes)

    except:
      done +=1
      continue

    # Strip out html tags
    def cleanhtml(raw_html):

      cleanr =re.compile('<.*?>')
      cleantext = re.sub(cleanr,'', raw_html)
      return cleantext;

    filth = cleanhtml(commentBody)+" - "+userName

    break

  if done == maxTries:
    errorString = "Sorry, They're busy killing kittens"
    return {"comment": errorString}
    
  else:
  # Return the horrible comment
    return {"comment": filth , "storyTitle": shortStoryURL, "numberOfLikes": upVotes, "numberOfDislikes": downVotes}

bottle.run(host='0.0.0.0', port=argv[1])

