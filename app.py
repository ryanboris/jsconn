#!/usr/bin/env python
from requests import get as GET
import requests
import pandas as pd
import sys
import credentials
import json


def parseLinkHeader(headers):
    links = {}
    if "link" in headers:
        linkHeaders = headers["link"].split(", ")
        for linkHeader in linkHeaders:
            (url, rel) = linkHeader.split("; ")
            url = url[1:-1]
            rel = rel[5:-1]
            links[rel] = url
    return links


def collect_things(endpoint):

    parameters = {"per_page": 100}

    response = GET(endpoint, parameters)

    link_headers = parseLinkHeader(response.headers)

    things = response.json()

    while 'next' in link_headers:
        response = GET(link_headers['next'], params=parameters)
        link_headers = parseLinkHeader(response.headers)
        things = things + response.json()

    return things


def app():
    user = sys.argv[1]
    repos_link = "https://api.github.com/users/{}/repos?client_id={}&client_secret={}".format(user, credentials.creds['CLIENT_ID'], credentials.creds['CLIENT_SECRET'])
    user_repos = requests.get(repos_link)
    repos = user_repos.json()
    while 'next' in user_repos.links.keys():
        user_repos = requests.get(user_repos.links['next']['url'])
        repos.extend(user_repos.json())
        repo_df = pd.DataFrame(repos)
    repo_names= list(repo_df['name'])
    langs = repo_df['language'].value_counts()
    lang_json = langs.to_json()
    reps = list(repo_names)
    punch_link = "https://api.github.com/repos/{}/{}/stats/punch_card".format(
            user, reps[1])
    punch_card = collect_things(punch_link)#punch card feature starts here
    punch_df = pd.DataFrame(punch_card, dtype='str')
    day= pd.Series(punch_df[0])
    # day= day.map({0: 'Sunday', 1: 'Monday', 2:'Tuesday', 3: 'Wednesday', 
    #                       4:'Thursday',5:'Friday', 6:'Saturday'})
    hour = pd.Series(punch_df[1])
    # hour = hour.map({0: '12 AM', 1: '1 AM', 2:'2 AM', 3: '3 AM', 4:'4 AM', 
    #                     5:'5 AM', 6:'6 AM', 7:'7 AM', 8:'8 AM', 9:'9 AM',
    #                     10: '10 AM', 11:'11 AM', 12: '12 PM', 13: '1 PM', 
    #                     14: '2 PM', 15: '3 PM', 16: '4 PM', 17: '5 PM', 
    #                     18: '6 PM', 19: '7 PM', 20: '8 PM', 21: '9 PM', 
    #                     22: '10 PM', 23: '11 PM'})
    commits = pd.Series(punch_df[2])
    assemble = pd.concat([day, hour, commits], axis=1)
    assemble.columns = ['Day','Hour','Commits']
    comms = assemble.to_json(orient='index')
    
    repo_df = pd.DataFrame(repos)
    langs = repo_df['language'].value_counts()
    lang_json = langs.to_json()
    print(lang_json)


app()