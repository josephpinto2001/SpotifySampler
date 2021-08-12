#!/usr/bin/env python
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests
import re
from dotenv import load_dotenv
import sys #TODO: implement ARGPARSE instead of sys 
import spotipy
import spotipy.util as util


def CreatePlaylist(username, song_title, song_artist,sp):
    # Create Appropriately Titled Empty Playlist For Samples
    playlist_name = f"Samples in {song_title} by {song_artist}"
    sp.user_playlist_create(username, name=playlist_name)
    print("Playlist Created.")
    return playlist_name


def main():

    load_dotenv() #get env variables

    if len(sys.argv) > 2: #TODO: change this to argparse
        username = sys.argv[1]
        url=sys.argv[2]
    else:
        print("Usage: %s username url" % (sys.argv[0],))
        sys.exit()

    #retrieve html info
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}
    r=requests.get(url,headers=headers)
    
    soup=BeautifulSoup(r.content,"html.parser")

    #finding input track info
    song_title=soup.find("meta",{"itemprop": "name"})["content"]
    song_artist=soup.find("span",{"itemprop": "byArtist"}).find("meta",{"itemprop": "name"})["content"]

    #finding sample track info
    candidateContainers=soup.find_all("header",{"class":"sectionHeader"})
    
    for container in candidateContainers:
        if container.find(text=re.compile("Contains samples")):
            theContainer=container
            break

    containers=theContainer.parent.find_all("div",{"class": "listEntry sampleEntry"})
    
    #extracting the title and artist for each track
    trackTuples=[]
    for container in containers:
        title=container.div.div.a.contents[0]
        artist=container.div.div.span.a.contents[0]
        trackTuples.append((title,artist))
    
    
    # print([a_tuple[0] for a_tuple in trackTuples])
    
    #initiating spotipy
    scope = 'playlist-modify-public'
    
    token=util.prompt_for_user_token(username,scope)
    if token:
        sp = spotipy.Spotify(auth=token)
    else:
        print("Can't get token for", username)
        return

    CreatePlaylist(username,song_title,song_artist,sp)


if __name__ == "__main__":
    main()