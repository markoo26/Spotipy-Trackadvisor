####!# Code Background ####!#

#!# Analyze track/album tempo~popularity dependence of one artist #!#
#!# On default the code is set to provide the analysis for the O.S.T.R. #!# 
#!# (Polish hip-hop artist) based on "Zycie po smierci". Firstly, there are simple #!#
#!# bar charts with tempo/popularity calculated . Secondly there is a request to the API #!#
#!# for the whole discography and the album can be compared among the other albums of #!#
#!# same artist #!#

####!# What do you need to run the code? ####!#

# Provide Spotify authentication data
# Provide the the link to the album you want to analyze 

####!# Navigation info. Use Ctrl + F with the following tags to run through ####!#

###### ==> 'Hashtagline' separates sections, which requires your input
####!# ==> Code sections
###!# ===> Code comments

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

webbrowser.open_new_tab("https://developer.spotify.com/")

#############################################################################################
client_id = "43c08ac2e88e47f8ac3623b927cd53d9"
client_secret = "15245bb31d594659a6b08d422be752cb"
scope = 'user-library-modify'
username = 'markpyt1992@gmail.com'
#############################################################################################

####!# Authentication and request for Spotify API token ####!#

token = util.prompt_for_user_token(username,scope, client_secret = client_secret, client_id = client_id, redirect_uri='http://google.com/')
spotify = spotipy.Spotify(auth = token)

####!# Get data about one single album ####!#

#############################################################################################
album_link = 'https://open.spotify.com/album/6iaT1pUYCfE4H0OATLDaJi?si=Fc6iLHlBQN6hhj7gBz9hjg'
#############################################################################################

####!# Extract basic data about the input album ####!#

album_object= spotify.album(album_link) ###!# Build album_object 
album_name = album_object.get("name") ###!# Extract the album title
album_artist = album_object.get("artists")[0].get("name") ###!# Extract album artist name
album_artist_id = album_object.get("artists")[0].get("id") ####!# Extract unique artist ID
total_tracks = album_object.get("total_tracks") ###!# Count tracks within an album ####!#

####!# Build pandas dataframe to store the album data ####!#

album_data = pd.DataFrame( {'Track Number': [], 'Title': [], 'Duration': [], 
                            'Tempo': [], 'Popularity': [], 'Danceability': [], 
                            'Energy': [], 'Instrumentalness': [], 'Liveness': [], 
                            'Loudness': [] }) 

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
    
    ####!# Append a row with complete data for every single track ####!# 

    album_data  = album_data.append({'Track Number': tt_nr, 'Title': ttl, 'Duration': drt, 'Tempo': tmp, 
                                     'Popularity': ppl, 'Danceability': dance, 'Energy': energy, 'Instrumentalness': instr, 
                                     'Liveness': live, 'Loudness': loud}, ignore_index = True)    

####!# Build the axes for charts ####!#

album_data = album_data.sort_values(by = 'Tempo', ascending = False) ###!# Sort values descending by tempo
tempos = album_data.iloc[:,3]
titles = album_data.iloc[:,1]
popularities = album_data.iloc[:,4]

####1# Clean titles of the tracks ####!#

re.compile('[^A-Za-z0-9_ ]+') ###!# Regex statement Used later to remove part 
                              ###!# beginning with '(feat)' from the title

for i in range(0, total_tracks):
    featuring = titles[i].find('feat')
    if featuring != - 1:
        titles[i] = titles[i][:featuring]
    else:
        pass
    
    titles[i] = re.sub('[^A-Za-z0-9_ ]+', '',titles[i])

####!# Simple barplot - tempo of each track ####!# 

f1 = plt.figure(1)

plt.bar(x = titles, height = tempos, data = tempos)
plt.ylabel(ylabel = "Track tempo")
plt.title(label = album_name)
plt.xticks(rotation=90)
plt.tight_layout()

####!# Popularity plot ####!#

f2 = plt.figure(2)

plt.bar(x = album_data["Title"], height = sorted(album_data["Popularity"]), data = sorted(album_data))
plt.ylabel(ylabel = "Track popularity")
plt.title(label = album_name)
plt.xticks(rotation=90)
plt.tight_layout()

####!# Correlation between variables ####!#

korelacje = album_data.corr()
plt.subplots(figsize=(12,9))
sns.heatmap(korelacje, vmax=0.9, square=True, annot=True)
plt.title('Correlation between audio features for the \n "' + album_name + '" album by ' + album_artist)

####!# Request the whole discography of the artist ####!#

request_address = "https://api.spotify.com/v1/artists/" + album_artist_id + "/albums" 
r = requests.get(request_address, headers={'Authorization': 'Authorization: Bearer ' + token})
discography = r.json()

total_albums = len(discography.get("items"))
discog_albums = []
discog_albums_id = []

####!# Loop that filters out singles and guest appearances from the discography ####!#
####!# Leaving only the full albums done by the artist ####!#

for i in range(0,total_albums):
    
    if discography.get("items")[i].get("album_group") == "album" and  discography.get("items")[i].get("album_type") == "album":
        discog_albums.append(discography.get("items")[i].get("name"))  
        discog_albums_id.append(discography.get("items")[i].get("id"))        

    else:
        pass

####!# Extract data from every single album from the discography ####!#

curr_album_data = pd.DataFrame({'Album Number': [], 'Album Name': [], 'Track Name': [], 
                                'TrackID': [], 'Tempo': [], 'Popularity': []})

for i in range(0,len(discog_albums_id)):

    curr_album = spotify.album(discog_albums_id[i])
    curr_album_name = curr_album.get("name")
    album_nr = str(i+1)
    
    for j in range(0, len(curr_album.get("tracks").get("items"))):

        cur_track_name = curr_album.get("tracks").get("items")[j].get("name")
        cur_track_id = curr_album.get("tracks").get("items")[j].get("id")
        curr_track = spotify.audio_analysis(cur_track_id)
        cur_track_tempo = curr_track.get("track").get("tempo")
        temp_track = spotify.track(cur_track_id)
        cur_track_pop = temp_track.get("popularity")
        curr_album_data  = curr_album_data.append({'Album Number': album_nr,
                                                   'Album Name': curr_album_name, 
                                                   'Track Name': cur_track_name, 
                                                   'TrackID': cur_track_id, 
                                                   'Tempo': cur_track_tempo,
                                                   'Popularity': cur_track_pop}, 
                                                    ignore_index = True)    

    discog_popularity = curr_album_data.groupby("Album Name").mean().iloc[:,1]

####!# Boxplots for tempos of each album of the artist combined with line plot ####!#
####!# of mean popularity of the tracks on the album ####!#

fig, ax1 = plt.subplots()

ax1.set_xlabel('Albums of the artist')
ax1.set_ylabel('Mean tempo of an album')
bxplot = sns.boxplot(x = curr_album_data["Album Name"], 
            y = curr_album_data["Tempo"])
plt.xticks(rotation = 90)
ax1.tick_params(axis='y', labelcolor = 'black')

ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

color = 'tab:blue'
ax2.set_ylabel('Mean popularity', color = 'black')
ax2.plot(discog_popularity, color = 'orangered')
ax2.tick_params(axis='y', labelcolor = 'orangered')
plt.xticks(rotation = 90)
plt.tight_layout()
plt.title('Tempo boxplot vs popularity lineplot for discography of ' + album_artist) 

end_time = time.time()
total_time = end_time - start_time
print(total_time)

