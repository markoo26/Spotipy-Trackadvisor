####!# Import of the Libraries ####!#

import pandas as pd, numpy as np, matplotlib.pyplot as plt, seaborn as sns
import spotipy.util as util
import spotipy
import os, requests, time, re, webbrowser
from requests.auth import HTTPBasicAuth

####!# Setting the working directory ####!#

start_time = time.time() ###!# Count code execution start time ###!#
                    
####!# Authentication variables ####!#
####!# Visit Spotify for Developers to get the access to the API ####!#

#webbrowser.open_new_tab("https://developer.spotify.com/")

#############################################################################################
client_id = "43c08ac2e88e47f8ac3623b927cd53d9"
client_secret = "15245bb31d594659a6b08d422be752cb"
scope = 'user-library-modify'
username = 'markpyt1992@gmail.com'
#############################################################################################

####!# Authentication and request for Spotify API token ####!#

token = util.prompt_for_user_token(username,scope, client_secret = client_secret, client_id = client_id, redirect_uri='http://google.com/')
spotify = spotipy.Spotify(auth = token)

### Get data from the first track ###

favourite_track = "https://open.spotify.com/track/5W40KI2BShi0k9YT0fIeMk?si=Easmy5veTIqcWM1VYmVhUA"
track_id = spotify.track(favourite_track).get("id")
TST_track_id = spotify.track(favourite_track).get("album").get("id")
dance = spotify.audio_features(tracks = [track_id])[0].get("danceability")
energy = spotify.audio_features(tracks = [track_id])[0].get("energy")
instr = spotify.audio_features(tracks = [track_id])[0].get("instrumentalness")
live = spotify.audio_features(tracks = [track_id])[0].get("liveness")
loud = spotify.audio_features(tracks = [track_id])[0].get("loudness")
accu= spotify.audio_features(tracks = [track_id])[0].get("acousticness")
speech = spotify.audio_features(tracks = [track_id])[0].get("speechiness")
valence = spotify.audio_features(tracks = [track_id])[0].get("valence")

track_vector = [dance,energy,instr,live,loud, accu, speech, valence]

### Get data from second track

sec_favourite_track = "https://open.spotify.com/track/6CXkgqe4C233tSa8yHYIm0?si=nv5ZZYLKTeuiBCudM9-uIQ"
sec_track_id = spotify.track(sec_favourite_track).get("id")

sec_dance = spotify.audio_features(tracks = [sec_track_id])[0].get("danceability")
sec_energy = spotify.audio_features(tracks = [sec_track_id])[0].get("energy")
sec_instr = spotify.audio_features(tracks = [sec_track_id])[0].get("instrumentalness")
sec_live = spotify.audio_features(tracks = [sec_track_id])[0].get("liveness")
sec_loud = spotify.audio_features(tracks = [sec_track_id])[0].get("loudness")
sec_accu= spotify.audio_features(tracks = [sec_track_id])[0].get("acousticness")
sec_speech = spotify.audio_features(tracks = [sec_track_id])[0].get("speechiness")
sec_valence = spotify.audio_features(tracks = [sec_track_id])[0].get("valence")

sec_track_vector = [sec_dance,sec_energy,sec_instr,sec_live,sec_loud]
((pd.DataFrame(track_vector) - pd.DataFrame(sec_track_vector)) ** 2).sum() ##0.742455

### Get data about whole album 

####!# Extract basic data about the input album ####!#

album_object= spotify.album(TST_track_id) ###!# Build album_object 
album_name = album_object.get("name") ###!# Extract the album title
album_artist = album_object.get("artists")[0].get("name") ###!# Extract album artist name
album_artist_id = album_object.get("artists")[0].get("id") ####!# Extract unique artist ID
total_tracks = album_object.get("total_tracks") ###!# Count tracks within an album ####!#

####!# Build pandas dataframe to store the album data ####!#

album_data = pd.DataFrame( {'Track Number': [], 'Title': [], 'Duration': [], 
                            'Tempo': [], 'Popularity': [], 'Danceability': [], 
                            'Energy': [], 'Instrumentalness': [], 'Liveness': [], 
                            'Loudness': [], 'Acousticness' : [], 'Speechiness': [],
                            'Valence' : []}) 

####!# Extract basic data about the input album ####!#

for i in range(0,total_tracks): ###!# For every single track in album get track:

    tt_nr = str(i) ###!# Number ###!#
    ttl = album_object.get("tracks").get("items")[i].get("name") ###!# Title ###!#
    drt = str(album_object.get("tracks").get("items")[i].get("duration_ms")) ###!# Duration ###!#
    track_id = album_object.get("tracks").get("items")[i].get('id') ###!# ID ###!#
    track_tempo = spotify.audio_analysis(track_id) 
    track_popularity = spotify.track(track_id) 
    tmp = track_tempo.get("track").get("tempo") ###!# Tempo ###!#
    ppl = track_popularity.get("popularity")
    
    ####!# Include data Spotify-specific descriptions every track using its ID ####!# 
    
    dance = spotify.audio_features(tracks = [track_id])[0].get("danceability")
    energy = spotify.audio_features(tracks = [track_id])[0].get("energy")
    instr = spotify.audio_features(tracks = [track_id])[0].get("instrumentalness")
    live = spotify.audio_features(tracks = [track_id])[0].get("liveness")
    loud = spotify.audio_features(tracks = [track_id])[0].get("loudness")
    accu = spotify.audio_features(tracks = [track_id])[0].get("acousticness")
    speech = spotify.audio_features(tracks = [track_id])[0].get("speechiness")
    valc = spotify.audio_features(tracks = [track_id])[0].get("valence")
    
    ####!# Append a row with complete data for every single track ####!# 

    album_data  = album_data.append({'Track Number': tt_nr, 'Title': ttl, 'Duration': drt, 
                                     'Tempo': tmp, 'Popularity': ppl, 'Danceability': dance, 
                                     'Energy': energy, 'Instrumentalness': instr, 
                                     'Liveness': live, 'Loudness': loud, 
                                     'Acousticness': accu, 'Speechiness': speech,
                                     'Valence': valc}, ignore_index = True)    

    
    cols = ['Danceability', 'Energy', 'Instrumentalness', 'Liveness', 'Loudness', 'Acousticness', 'Speechiness', 'Valence']
    album_data["Features"] = album_data[cols].values.tolist() 
#    album_data["Dissimilarity"] = ((pd.DataFrame(track_vector) - pd.DataFrame(album_data["Features"])) ** 2).sum()
    dissimilarity = 0    
    album_data["Dissimilarity"] = 1.25
    
    weights = []
    
    for i in range(0,len(cols)):
        weights.append(input("Rank the importance of the feature (from 1-10) for feature: " + cols[i] + ": "))
    
    weights = pd.DataFrame(weights, index = cols)
    weights = weights.astype(int)
    weights = weights/ weights.sum()
       
    
    ### Print radar chart with preferences

    for i in range(0,len(album_data)):
       for j in range(0,5):
           dissimilarity = ((track_vector[j] - album_data["Features"][i][j]) ** 2) * weights[0][j]
           print(dissimilarity)
       album_data["Dissimilarity"][i] = dissimilarity 
       
columns = ["Title", "Dissimilarity"]
print(album_data[columns].sort_values(by="Dissimilarity").head())


 