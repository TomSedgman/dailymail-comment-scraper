#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib
import urllib.error
import urllib.request
import urllib.parse
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
from sys import argv
import base64
import re
import lxml
import xmltodict
from lxml import objectify
import simplejson as json
import bottle
from bottle import default_app, request, route, response, get
from random import randint
import csv

bottle.debug(True)

@get('/')
def index():
    response.content_type = 'text/json; charset=utf-8'

    # Function to get json data from a url
    def get_jsonparsed_data(url):
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"}
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req) as response:
                data = response.read()
        except urllib.error.HTTPError as err:
            print("The server failed to complete the request with error ")
            print(err.code)
        except urllib.error.URLError as err:
            print('We failed to reach the server.')
            print('Reason: ', err.reason)

        returnedJson = json.loads(data)
        return returnedJson

    # Function to get xml data as json from a url:
    def get_xml(request):

        req = urllib.request.Request(request)
        try:
            with urllib.request.urlopen(req) as response:
                data = response.read()
        except urllib.error.URLError as err:
            print ("Couldn't reach the Daily Mail's RSS feed")
            print(err.reason)
        except urllib.error.HTTPError as err:
            print("The server failed to complete the request with error ")
            print(err.code)
        xmlData = xmltodict.parse(data)
        return xmlData

    # URL for Daily Mail's RSS feed:
    urlArticleList = "http://www.dailymail.co.uk/home/index.rss"

    # How many times to retry
    done = 0
    maxTries = 5

    while done < maxTries:

        # Get all stories from the rss feed
        try:
            xmlDataStories = get_xml(urlArticleList)
            jsonDataStories = json.dumps(xmlDataStories)
            jsonDataStoriesLoaded = json.loads(jsonDataStories)

        except:
            done += 1

        # Pick random story
        try:
            storiesNumber = len(
                jsonDataStoriesLoaded["rss"]["channel"]["item"])
            storyNumber = randint(0, (storiesNumber - 1))

        except:
            done += 1

        # Get the Stpry ID and clean up the URL
        try:
            storyURL = jsonDataStoriesLoaded["rss"]["channel"]["item"][storyNumber]["link"]
            shortStoryURL = storyURL.split('?', 1)[0]
            storyIDAlmost = shortStoryURL.split('-', 1)[-1]
            storyID = storyIDAlmost.split('/', 1)[0]

        except:
            done += 1

        # Maximum Number of comments we want to get from the API
        maxCommentNumber = str(20)

        # Build the URL to return the 'Best Rated' comments for the random story
        try:
            urlForComments = "http://www.dailymail.co.uk/reader-comments/p/asset/readcomments/" + \
                storyID+"?max="+maxCommentNumber+"&sort=voteRating&order=desc"
        except:
            done += 1

        # Get comment and metadata
        try:
            jsonDataComments = get_jsonparsed_data(urlForComments)
            filename = jsonDataComments["payload"]["page"][0]["assetHeadline"]
            fields = ["User Name", "User Location","Message","Upvotes","Downvotes","Published","Comment"]
            commentsNumber = len(jsonDataComments["payload"]["page"])
            randomCommentNumber = 0
            
            f = open(filename,'w')
            writer = csv.writer(f)
            writer.writerow(fields) 

            while randomCommentNumber < commentsNumber:
                
                downVotes = int((jsonDataComments["payload"]["page"][randomCommentNumber]["voteCount"] - jsonDataComments["payload"]["page"][randomCommentNumber]["voteRating"]) * 0.5)
                row = [jsonDataComments["payload"]["page"][randomCommentNumber]["userAlias"],jsonDataComments["payload"]["page"][randomCommentNumber]["userLocation"],jsonDataComments["payload"]["page"][randomCommentNumber]["message"],int(jsonDataComments["payload"]["page"][randomCommentNumber]["voteRating"] + downVotes),downVotes,jsonDataComments["payload"]["page"][randomCommentNumber]["dateCreated"]]
                writer.writerow(row)
                randomCommentNumber +=1
            
            f.close()
            commentBody = jsonDataComments["payload"]["page"][randomCommentNumber]["message"]
            userName = jsonDataComments["payload"]["page"][randomCommentNumber]["userAlias"]
            
        except:
            done += 1
            continue

        # Strip out html tags
        def cleanhtml(raw_html):

            cleanr = re.compile('<.*?>')
            cleantext = re.sub(cleanr, '', raw_html)
            return cleantext

        try:
            filth = cleanhtml(commentBody)+" - "+userName
        except:
            print ("Error parsing contet")
            done += 1
            continue
        break

    if done == maxTries:
        errorString = "Sorry, no comments - they're busy killing kittens"
        return {"comment": errorString}

    else:
        # Return the horrible comment
        return jsonDataComments

bottle.run(host='0.0.0.0', port=argv[1], reloader=True)
