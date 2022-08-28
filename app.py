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


        # Build the URL to return the 'Best Rated' comments for the random story
        try:
            urlForComments = "http://www.dailymail.co.uk/reader-comments/p/asset/readcomments/"+request.query_string+"?max=20000&sort=voteRating&order=desc"
        except:
            done += 1

        # Get comment and metadata
        try:
            jsonDataComments = get_jsonparsed_data(urlForComments)
            commentsNumber = len(jsonDataComments["payload"]["page"])
            randomCommentNumber = 0
            downVotes = int((jsonDataComments["payload"]["page"][randomCommentNumber]["voteCount"] - jsonDataComments["payload"]["page"][randomCommentNumber]["voteRating"]) * 0.5)
            comment = {
                    "User Name": jsonDataComments["payload"]["page"][randomCommentNumber]["userAlias"],
                    "User Location": jsonDataComments["payload"]["page"][randomCommentNumber]["userLocation"],
                    "Message": jsonDataComments["payload"]["page"][randomCommentNumber]["message"],
                    "Upvotes": int(jsonDataComments["payload"]["page"][randomCommentNumber]["voteRating"] + downVotes),
                    "Downvotes": downVotes,
                    "Published": jsonDataComments["payload"]["page"][randomCommentNumber]["dateCreated"],
                }
            output = {
                "Title": jsonDataComments["payload"]["page"][0]["assetHeadline"],
                # "Comment "+randomCommentNumber+1: comment                
            }
            # while randomCommentNumber < commentsNumber:
            #     # randomCommentNumber = randint(0, (commentsNumber - 1))  
            #     downVotes = int((jsonDataComments["payload"]["page"][randomCommentNumber]["voteCount"] - jsonDataComments["payload"]["page"][randomCommentNumber]["voteRating"]) * 0.5)
            #     comment = {
            #         "User Name": jsonDataComments["payload"]["page"][randomCommentNumber]["userAlias"],
            #         "User Location": jsonDataComments["payload"]["page"][randomCommentNumber]["userLocation"],
            #         "Message": jsonDataComments["payload"]["page"][randomCommentNumber]["message"],
            #         "Upvotes": int(jsonDataComments["payload"]["page"][randomCommentNumber]["voteRating"] + downVotes),
            #         "Downvotes": downVotes,
            #         "Published": jsonDataComments["payload"]["page"][randomCommentNumber]["dateCreated"]
            #     }
            #     z = json.loads(output)
            #     z.update(comment)
            #     randomCommentNumber +=1
        except:
            done += 1
            continue

        # Strip out html tags
        # def cleanhtml(raw_html):

        #     cleanr = re.compile('<.*?>')
        #     cleantext = re.sub(cleanr, '', raw_html)
        #     return cleantext

        # try:
        #     filth = cleanhtml(commentBody)+" - "+userName
        # except:
        #     print ("Error parsing contet")
        #     done += 1
        #     continue
        # break

    if done == maxTries:
        errorString = "Sorry, no comments - they're busy killing kittens"
        return {"comment": errorString}

    else:
        # Return the horrible comment
        return {"page":comment}
        # return {"storyTitle": shortStoryURL, "": userName, "comment": filth, "numberOfLikes": upVotes, "numberOfDislikes": downVotes}

bottle.run(host='0.0.0.0', port=argv[1], reloader=True)
