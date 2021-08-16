#!/usr/bin/env python
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import argparse
import requests
import re
from dotenv import load_dotenv
import spotipy
import spotipy.util as util
from fuzzywuzzy import fuzz
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

chromedriver_PATH='<LOCAL PATH TO CHROMEDRIVER>'

def getURL(title,artist):
    driver=webdriver.Chrome(chromedriver_PATH)
    title.replace(" ","+")
    artist.replace(" ","+")
    driver.get(f"https://www.whosampled.com/search/?q={title}+{artist}")

    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "trackTitle"))
            )
        element.click()
    except:
        driver.quit()
        print("couldn't find song on Whosampled!")
    
    url=driver.current_url
    driver.quit()
    return str(url)

def CreatePlaylist(username, song_title, song_artist,sp):
    #creating empty playlist with custom name
    playlist_title = f"Samples in {song_title} by {song_artist}"
    playlist=sp.user_playlist_create(username, name=playlist_title)
    print("Playlist Created.")
    return playlist["id"]

def GetTrackIDs(sample_data,sp):
    track_IDS=[]
    
    for Tuple in sample_data:
        artist=Tuple[1]
        title=Tuple[0]
        results=sp.search(q=f"{title} {artist}", limit=5,type='track')
        if results['tracks']['total'] == 0: #can't find track on spotify, go to next track
            continue
        
        for result in range(len(results['tracks']['items'])): #fuzzy matching accounts for non-exact matchings of title/artist
                artist_similarity=fuzz.token_set_ratio(results['tracks']['items'][result]['artists'][0]['name'], artist)
                title_similarity=fuzz.token_set_ratio(results['tracks']['items'][result]['name'], title) 
    
                if  artist_similarity> 90 and title_similarity > 90: 
                    track_IDS.append(results['tracks']['items'][result]['id']) 
                    break
    return track_IDS


def main():

    load_dotenv() #get env variables

    #get args with argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("username", help="numerical Spotify account username",
                        type=str)
    parser.add_argument("input_title", help="title of input song",
                        type=str)
    parser.add_argument("input_artist", help="artist of input song",
                        type=str)
    args = parser.parse_args()

    username = args.username
    input_title= args.input_title
    input_artist= args.input_artist

    #get url info
    url=getURL(input_title,input_artist)
    #retrieve html info
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}
    r=requests.get(url,headers=headers)
    
    soup=BeautifulSoup(r.content,"html.parser")

    #finding input track info
    song_title=soup.find("meta",{"itemprop": "name"})["content"]
    song_artist=soup.find("span",{"itemprop": "byArtist"}).find("meta",{"itemprop": "name"})["content"]

    #finding sample track info
    candidateContainers=soup.find_all("header",{"class":"sectionHeader"})
    
    theContainer=None

    for container in candidateContainers:
        if container.find(text=re.compile("Contains samples")):
            theContainer=container
            break
    if not theContainer:
        print(f"{song_title} {song_artist} has no samples")
        exit()
    containers=theContainer.parent.find_all("div",{"class": "listEntry sampleEntry"})
    
    #extracting the title and artist for each track
    trackTuples=[]

    # add input song at top of playlist
    trackTuples.append((song_title,song_artist))

    for container in containers:
        title=container.div.div.a.contents[0]
        artist=container.div.div.span.a.contents[0]
        trackTuples.append((title,artist))
    
    #initiating spotipy
    scope = 'playlist-modify-public'
    
    token=util.prompt_for_user_token(username,scope)
    if token:
        sp = spotipy.Spotify(auth=token)
    else:
        print("Can't get token for", username)
        return

    playlist_id=CreatePlaylist(username,song_title,song_artist,sp) #create new playlist with custom name
    track_ids=GetTrackIDs(trackTuples,sp) #looking up track titles and artists in spotify database
    sp.user_playlist_add_tracks(username,playlist_id,track_ids) #populating playlist with tracks
    return
if __name__ == "__main__":
    main()