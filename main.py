import json
from flask import Flask, request, redirect, g, render_template, url_for, session
import requests
from urllib.parse import quote
import pandas as pd
from sklearn.cluster import KMeans
import sklearn as sk
from collections import Counter, defaultdict
import numpy as np
from random import randrange
from random import randint
import random
import string 
import spotipy
import spotipy.util as util
from sklearn.preprocessing import MinMaxScaler
from flask_sessionstore import Session
from clusterfy_functions import get_track_info, clusterfy_function


app = Flask(__name__)

SESSION_TYPE = 'redis'
app.config.from_object(__name__)
Session(app)

def randomword(length):
   letters = string.ascii_lowercase
   return ''.join(random.choice(letters) for i in range(length))

secret_user = randomword(100)
app.config['SECRET_KEY'] = secret_user

####################################################################################################
client_id = "XXXXXXXXXXXXX"
client_secret = "XXXXXXXXXXXXXXXX"

spotify_authentification_url = "https://accounts.spotify.com/authorize"
spotify_token_url = "https://accounts.spotify.com/api/token"
spotify_base_url = "https://api.spotify.com"
api_version = "v1"
spotify_api_url = "{}/{}".format(spotify_base_url, api_version)

client_url = "http://127.0.0.1"
port = 8080
redir_url = "{}:{}/callback/q".format(client_url, port)
scope = "playlist-modify-public playlist-modify-private user-top-read user-library-read playlist-read-private playlist-read-collaborative"
state = ""

auth_query_parameters = {
    "response_type": "code",
    "redirect_uri": redir_url,
    "scope": scope,
    "client_id": client_id
}
#####################################################################################################

@app.route("/", methods=["GET", "POST"])
def intro():

    return render_template("first_page.html")


@app.route("/auth", methods=["GET", "POST"])
def index():
    #authorize user
    url_args = "&".join(["{}={}".format(key, quote(val)) for key, val in auth_query_parameters.items()])
    auth_url = "{}/?{}".format(spotify_authentification_url, url_args)

    return redirect(auth_url)


@app.route("/info", methods=["GET", "POST"])
def info():
   

    return render_template("info.html")


@app.route("/callback/q", methods=["GET", "POST"])
def callback():
    #get acess_tokens for spotipy and authorization header for requests.get
    auth_token = request.args['code']
    code_payload = {
        "grant_type": "authorization_code",
        "code": str(auth_token),
        "redirect_uri": redir_url,
        'client_id': client_id,
        'client_secret': client_secret,
    }
    post_request = requests.post(spotify_token_url, data=code_payload)
    response_data = json.loads(post_request.text)
    access_token = response_data["access_token"]

    session["a_t"] = access_token
    authorization_header = {"Authorization": "Bearer {}".format(access_token)}
    session["a_h"] = authorization_header

    return render_template("type.html")


@app.route("/callback/qnewsongs", methods=["GET", "POST"])
def new_songs():
    #Authorization
    authorization_header = session.get("a_h")
    playlist_api_endpoint = "{}/me/top/artists?time_range=medium_term&limit=100".format(spotify_api_url)
    playlists_response = requests.get(playlist_api_endpoint, headers=authorization_header)
    top_100_artists = json.loads(playlists_response.text)

    ##Extracting top 100 artists info
    top100_length = len(top_100_artists["items"])
    top_artists_names_list = []
    for n in range(top100_length):
        top100_artists_names = top_100_artists["items"][n]["name"]
        top_artists_names_list.append(top100_artists_names)

    top_artists_uri_list = []
    for n in range(top100_length):
        top100_artists_uris = top_100_artists["items"][n]["id"]
        top_artists_uri_list.append(top100_artists_uris)

    top_artists_popularity_list = []
    for n in range(top100_length):
        top100_artists_pop = top_100_artists["items"][n]["popularity"]
        top_artists_popularity_list.append(top100_artists_pop)

    top_artists_images_list = []
    for i in range(top100_length):
        top_100_images = top_100_artists["items"][i]["images"][0]["url"]
        top_artists_images_list.append(top_100_images)

    top_artists_list_for_unpacking = list(zip(top_artists_names_list, top_artists_uri_list, top_artists_images_list))

    ##store top artists info in redis server for use later
    session["top_artists"] =  top_artists_uri_list
    session["artists_pop"] =  top_artists_popularity_list
    
    return render_template("top_artists_select.html", sorted_array = top_artists_list_for_unpacking)

@app.route("/callback/discover_playlist", methods=["GET", "POST"])
def discover_playlist():
    access_token = session.get("a_t")
    sp = spotipy.Spotify(auth=access_token)
    top_artists_popularity = session.get("artists_pop")
    top_artists_ids = session.get("top_artists")

    #get selected artists info 
    ####################################################################################################
    #get user selected artist ids
    if request.method == "POST":
        selected_artists_ids = request.form.getlist("checkbox_my")
        selected_artists_ids = np.array(selected_artists_ids)
    #if user selects no artiss show an error page
    if selected_artists_ids.size == 0:
            return render_template("error_page3.html")
    
    #get popularity of selected artists
    all_selected_artists_popularity = np.array([])
    for i in range(len(selected_artists_ids)):
        selected_artists_popularity = np.array(top_artists_popularity)[np.where(np.array(top_artists_ids) == selected_artists_ids[i])[0]]
        all_selected_artists_popularity = np.append(all_selected_artists_popularity, selected_artists_popularity)
    mean_top_artist_popularity = np.mean(all_selected_artists_popularity)
    ####################################################################################################

    
    ##do two runs of related artists (find artists related to the selected artists and artists related to those artists)
    ####################################################################################################
    related_artists_ids_first_run = np.array([])
    related_artists_pop_first_run = np.array([])

    for i in range(len(selected_artists_ids)):
        related_artists = sp.artist_related_artists(selected_artists_ids[i])
        related_artists_length = len(related_artists["artists"])
        for n in range(related_artists_length):
            related_artists_name = related_artists["artists"][n]["id"]
            related_artists_ids_first_run = np.append(related_artists_ids_first_run, related_artists_name)
   
        for n in range(related_artists_length):
            related_artists_name = related_artists["artists"][n]["popularity"]
            related_artists_pop_first_run = np.append(related_artists_pop_first_run, related_artists_name)


    related_artists_ids_second_run = np.array([])
    related_artists_pop_second_run = np.array([])

    for i in range(len(related_artists_ids_first_run)):
        related_artists = sp.artist_related_artists(related_artists_ids_first_run[i])
        related_artists_length = len(related_artists["artists"])
        
        for n in range(related_artists_length):
            related_artists_name = related_artists["artists"][n]["id"]
            related_artists_ids_second_run =  np.append(related_artists_ids_second_run, related_artists_name)
            
        for n in range(related_artists_length):
            related_artists_name = related_artists["artists"][n]["popularity"]
            related_artists_pop_second_run = np.append(related_artists_pop_second_run, related_artists_name)


    #combine info from both runs
    complete_related_artists_ids = np.concatenate((related_artists_ids_first_run, related_artists_ids_second_run), axis = None)
    complete_related_artists_popularity = np.concatenate((related_artists_pop_first_run, related_artists_pop_second_run), axis = None)
    ####################################################################################################

    #multiple the mean popularity of selected artists by a constant .8 this will be a new 
    #treshold for popularity. Essentially finds artists that are .8 times less popular than the average 
    #of the user selected artists.
    ####################################################################################################
    new_treshold = mean_top_artist_popularity * 0.8
    #if popularity is too low then bring it back to 62
    if new_treshold < 60:
        new_treshold = 62

    #get artist ids for those who are lower than the new treshold
    low_popularity_artist_ids = complete_related_artists_ids[complete_related_artists_popularity < new_treshold]
    low_popularity_artist_ids = np.unique(low_popularity_artist_ids)


    ##get songs of the low popularity artists
    low_pop_artists_song_ids = np.array([])
    for i in range(len(low_popularity_artist_ids)):
        current_artist_top_songs = sp.artist_top_tracks(low_popularity_artist_ids[i], country='US')
    
        for n in range(len(current_artist_top_songs["tracks"])):
            low_pop_artists_top_songs_ids = current_artist_top_songs["tracks"][n]["id"]
            low_pop_artists_song_ids = np.append(low_pop_artists_song_ids,low_pop_artists_top_songs_ids)

    if len(low_pop_artists_song_ids) < 100:
        new_treshold = mean_top_artist_popularity * 0.75
        if new_treshold < .65:
            new_treshold = 70

        low_popularity_artist_ids = complete_related_artists_ids[complete_related_artists_popularity < new_treshold]
        low_popularity_artist_ids = np.unique(low_popularity_artist_ids)

        low_pop_artists_song_ids = np.array([])
        for i in range(len(low_popularity_artist_ids)):

            current_artist_top_songs = sp.artist_top_tracks(low_popularity_artist_ids[i], country='US')    
            for n in range(len(current_artist_top_songs["tracks"])):
                low_pop_artists_top_songs_ids = current_artist_top_songs["tracks"][n]["id"]
                low_pop_artists_song_ids = np.append(low_pop_artists_song_ids,low_pop_artists_top_songs_ids)
    
    #limit the maximum number of songs to 900
    random_samp_indices = np.random.choice(np.arange(0,899), 900)

    if len(low_pop_artists_song_ids) > 901:
        session["low_pop_artist_song_ids"] = list(low_pop_artists_song_ids[random_samp_indices])
    else:
        session["low_pop_artist_song_ids"] = list(low_pop_artists_song_ids)

    low_pop_artists_song_names = np.array([])
    for i in range(len(low_popularity_artist_ids)):
        current_artist_top_songs = sp.artist_top_tracks(low_popularity_artist_ids[i])
        for n in range(len(current_artist_top_songs["tracks"])):
            low_pop_artists_top_songs_ids = current_artist_top_songs["tracks"][n]["name"]
            low_pop_artists_song_names = np.append(low_pop_artists_song_names, low_pop_artists_top_songs_ids)

    if len(low_pop_artists_song_ids) > 901:
        session["low_pop_artist_song_names"] = list(low_pop_artists_song_names[random_samp_indices])
    else:
        session["low_pop_artist_song_names"] = list(low_pop_artists_song_names)
    ####################################################################################################


    #create objects for audio features and their icons
    ####################################################################################################
    icons = ["/static/acoustic.png", "/static/dance.png","/static/energy.png",
        "/static/instrument.png","/static/live.png","/static/loud.png",
        "/static/speech.png","/static/tempo.png","/static/happy.png"]

    icons2 = ["/static/acoustic1.png", "/static/dance1.png","/static/energy1.png",
        "/static/instrument1.png","/static/live1.png","/static/loud1.png",
        "/static/speech1.png","/static/tempo1.png","/static/happy1.png"]

    
    low_features_index = range(9)
    low_feature_names = ['acousticness', 'danceability', "energy", 
    'instrumentalness', 'liveness', 'loudness', 'speechiness','tempo', 'valence']

    high_features_index = range(9)
    high_feature_names = ['acousticness', 'danceability', "energy", 
    'instrumentalness', 'liveness', 'loudness', 'speechiness','tempo', 'valence']

    low_feats_with_icons = list(zip(low_feature_names, low_features_index, icons2 ))   
    high_feats_with_icons = list(zip(high_feature_names, high_features_index, icons )) 
    ####################################################################################################

    return render_template("feature_selection2.html", low_features_dict= low_feats_with_icons,high_features_dict = high_feats_with_icons)



@app.route("/callback/playlist_showcase_low_pop", methods=["GET", "POST"])
def callback_feat_sel_low_pop():
    #get the access token 
    access_token = session.get("a_t")
    sp = spotipy.Spotify(auth=access_token)

    #get the low popularity artists song names and ids
    low_pop_songs =  session.get("low_pop_artist_song_names")
    low_pop_ids = session.get("low_pop_artist_song_ids")

##################################################################################################################################
    if request.method == 'POST':
        #Generate a playlist without sound features if the user picks this option
        #In this case randomly select 50 songs
        if request.form.get('sub') == "Generate Playlist Without Sound Features":
              
                no_feats_index1 = random.sample(range(len(low_pop_songs)), 50)
                no_feats_index2 = random.sample(range(len(low_pop_songs)), 50)
                no_feats_index3 = random.sample(range(len(low_pop_songs)), 50)

                first_best_tracks = [low_pop_songs[i] for i in no_feats_index1]
                second_best_tracks = [low_pop_songs[i] for i in no_feats_index2]
                third_best_tracks = [low_pop_songs[i] for i in no_feats_index3]

                first_best_tracks_uris = [low_pop_ids[i] for i in no_feats_index1]
                second_best_tracks_uris = [low_pop_ids[i] for i in no_feats_index2]
                third_best_tracks_uris = [low_pop_ids[i] for i in no_feats_index3]

                best_playlists_list = list()
                best_playlists_list.append(first_best_tracks)
                best_playlists_list.append(second_best_tracks)
                best_playlists_list.append(third_best_tracks)


                ##Get artist names, track ids and images for playlist 1
                ids_best_playlist_1 = list(first_best_tracks_uris)
                best_playlist_1_track_info_list1 = sp.tracks(ids_best_playlist_1)

                best_playlist_1_artists = []
                for i in range(len(best_playlist_1_track_info_list1["tracks"])):
                    c_a = best_playlist_1_track_info_list1["tracks"][i]["artists"][0]["name"]
                    best_playlist_1_artists.append(c_a)

                best_playlist_1_artists_ids = []
                for i in range(len(best_playlist_1_track_info_list1["tracks"])):
                    c_a = best_playlist_1_track_info_list1["tracks"][i]["id"]
                    best_playlist_1_artists_ids.append(c_a)

                best_playlist_1_images = []
                for i in range(len(best_playlist_1_track_info_list1["tracks"])):
                    c_a = best_playlist_1_track_info_list1["tracks"][i]["album"]["images"][0]["url"]
                    best_playlist_1_images.append(c_a)


                ##Get artist names, track ids and images for playlist 2
                ids_best_playlist_2 = list(second_best_tracks_uris)
                best_playlist_2_track_info_list1 = sp.tracks(ids_best_playlist_2)

                best_playlist_2_artists = []
                for i in range(len(best_playlist_2_track_info_list1["tracks"])):
                    c_a = best_playlist_2_track_info_list1["tracks"][i]["artists"][0]["name"]
                    best_playlist_2_artists.append(c_a)

                best_playlist_2_artists_ids = []
                for i in range(len(best_playlist_2_track_info_list1["tracks"])):
                    c_a = best_playlist_2_track_info_list1["tracks"][i]["id"]
                    best_playlist_2_artists_ids.append(c_a)

                best_playlist_2_images = []
                for i in range(len(best_playlist_2_track_info_list1["tracks"])):
                    c_a = best_playlist_2_track_info_list1["tracks"][i]["album"]["images"][0]["url"]
                    best_playlist_2_images.append(c_a)

                
                ##Get artist names, track ids and images for playlist 3
                ids_best_playlist_3 = list(third_best_tracks_uris)
                best_playlist_3_track_info_list1 = sp.tracks(ids_best_playlist_3)

                best_playlist_3_artists = []
                for i in range(len(best_playlist_3_track_info_list1["tracks"])):
                    c_a = best_playlist_3_track_info_list1["tracks"][i]["artists"][0]["name"]
                    best_playlist_3_artists.append(c_a)

                best_playlist_3_artists_ids = []
                for i in range(len(best_playlist_3_track_info_list1["tracks"])):
                    c_a = best_playlist_3_track_info_list1["tracks"][i]["id"]
                    best_playlist_3_artists_ids.append(c_a)

                best_playlist_3_images = []
                for i in range(len(best_playlist_3_track_info_list1["tracks"])):
                    c_a = best_playlist_3_track_info_list1["tracks"][i]["album"]["images"][0]["url"]
                    best_playlist_3_images.append(c_a)


                #combine all of the needed playlist info together for each playlist
                best_playlist_3_full_list = list(zip(best_playlist_3_images, third_best_tracks, best_playlist_3_artists, third_best_tracks_uris))
                best_playlist_2_full_list = list(zip(best_playlist_2_images, second_best_tracks, best_playlist_2_artists, second_best_tracks_uris))
                best_playlist_1_full_list = list(zip(best_playlist_1_images, first_best_tracks, best_playlist_1_artists, first_best_tracks_uris))

                best_playlists_full_list = list()
                best_playlists_full_list.append(best_playlist_1_full_list)
                best_playlists_full_list.append(best_playlist_2_full_list)
                best_playlists_full_list.append(best_playlist_3_full_list)
                
                ##save one big list of playlist info on redis server for later use
                session["best_p_list"] = best_playlists_full_list

                return render_template("playlist_showcase.html", first_best_tracks = best_playlist_1_full_list, 
                second_best_tracks = best_playlist_2_full_list, third_best_tracks = best_playlist_3_full_list)

##################################################################################################################################



    ##this runs if the user selected audio features
##################################################################################################################################
    ##defne audio feature names
    low_feature_names = ['acousticness', 'danceability', "energy", 
    'instrumentalness', 'liveness', 'loudness', 'speechiness','tempo', 'valence']

    high_feature_names = ['acousticness', 'danceability', "energy", 
    'instrumentalness', 'liveness', 'loudness', 'speechiness','tempo', 'valence']

    ##get audio features selected by the user
    if request.method == "POST":
        selected_high_features_inds = request.form.getlist("high_features_checkbox")
        selected_low_features_inds = request.form.getlist("low_features_checkbox")

        if not selected_high_features_inds and not selected_low_features_inds:
            return render_template("error_page_2.html")

        selected_high_features_inds = list(map(int, selected_high_features_inds))
        selected_low_features_inds = list(map(int, selected_low_features_inds))
        
        MaxFeatures = [high_feature_names[i] for i in selected_high_features_inds]
        MinFeatures = [low_feature_names[i] for i in selected_low_features_inds]
        
    user_choice_dict = {"low_features": [1], "high_features": [1]}

    final_selected_high_features = np.zeros(1)
    final_selected_low_features = np.zeros(1)

    if not MaxFeatures:
        final_selected_high_features[0] = 1
    else:
        final_selected_high_features = np.array(MaxFeatures)

    if not MinFeatures:
        final_selected_low_features[0] = 1
    else:
        final_selected_low_features = np.array(MinFeatures)

    ##if users dont select any features then return an error page
    if bool(set(selected_high_features_inds) & set(selected_low_features_inds)):
        return render_template("error_page_2.html")
      
    ##Get track info from redis server
    authorization_header = session.get("a_h")
    all_needed_track_names = session.get("low_pop_artist_song_names")
    all_needed_track_ids = session.get("low_pop_artist_song_ids")

    number_of_tracks_chosen = len(all_needed_track_names)  
    track_features_list = []

    ##get audio features for eacb track
    for d in range(len(all_needed_track_ids)):
            current_track_id = all_needed_track_ids[d]
            playlist_api_endpoint = "{}/audio-features/{}".format(spotify_api_url, current_track_id)
            playlists_response = requests.get(playlist_api_endpoint, headers=authorization_header)

            track_features = json.loads(playlists_response.text)
            track_features_list.append(track_features)


    total_features_flat = np.zeros(0)
    condition = "none"
    if(final_selected_low_features[0] != 1. and final_selected_high_features[0] != 1.):
        total_features_flat = np.concatenate((final_selected_low_features, final_selected_high_features), axis=None)
        condition = "both"
    elif(final_selected_low_features[0] == 1 and final_selected_high_features[0] != 1):
        total_features_flat = final_selected_high_features.copy()
        condition = "max"
    elif(final_selected_low_features[0] != 1 and final_selected_high_features[0] == 1):
        total_features_flat = final_selected_low_features.copy()
        condition = "min"


    ##make a dataframe with tracks informations
    track_features_DF = pd.DataFrame(track_features_list)
    track_features_DF['track_names'] = all_needed_track_names
    track_features_DF_filtered_for_clustering = track_features_DF[total_features_flat]

    track_features_DF_filtered_for_clustering_scaled = sk.preprocessing.scale(track_features_DF_filtered_for_clustering)
    track_features_DF_filtered_for_clustering_scaled = pd.DataFrame(track_features_DF_filtered_for_clustering_scaled)
    
    track_features_DF_filtered_for_clustering_scaled = track_features_DF_filtered_for_clustering_scaled.drop_duplicates(keep="first")
    track_features_DF_filtered_for_clustering_scaled = track_features_DF_filtered_for_clustering_scaled.replace([np.inf, -np.inf], np.nan)
    track_features_DF_ready_for_clustering = track_features_DF_filtered_for_clustering_scaled.dropna()
        



    ##run the clusterfy Kmeans function on the dataframe
    ##this returns 3 lists of tracks and relevant info,  corresponding to the user's feature selection
    first_best_pst, second_best_pst, third_best_pst = clusterfy_function(track_features_DF,track_features_DF_ready_for_clustering,final_selected_low_features, final_selected_high_features, condition = condition)

    ##extract track names      
    first_best_tracks = first_best_pst["track_names"]
    second_best_tracks = second_best_pst["track_names"]
    third_best_tracks = third_best_pst["track_names"]
    #extract track uris
    first_best_tracks_uris = list(first_best_pst["uri"])
    second_best_tracks_uris = list(second_best_pst["uri"])
    third_best_tracks_uris = list(third_best_pst["uri"])

    best_playlists_list = list()
    best_playlists_list.append(first_best_tracks)
    best_playlists_list.append(second_best_tracks)
    best_playlists_list.append(third_best_tracks)

    best_playlists_uris_list = list()
    best_playlists_uris_list.append(first_best_tracks_uris)
    best_playlists_uris_list.append(second_best_tracks_uris)
    best_playlists_uris_list.append(third_best_tracks_uris)

    

    access_token = session.get("a_t")
    sp = spotipy.Spotify(auth=access_token) 

    ids_best_playlist_1 = [i.split('track:', 1)[1] for i in first_best_tracks_uris]
    ids_best_playlist_2 = [i.split('track:', 1)[1] for i in second_best_tracks_uris]
    ids_best_playlist_3 = [i.split('track:', 1)[1] for i in third_best_tracks_uris]

    #run the get track info on the track ids to get artist names and album images.
    best_playlist_1_artists, best_playlist_1_images = get_track_info(ids_best_playlist_1, access_token)
    best_playlist_2_artists, best_playlist_2_images = get_track_info(ids_best_playlist_2, access_token)
    best_playlist_3_artists, best_playlist_3_images = get_track_info(ids_best_playlist_3, access_token)

    best_playlist_3_full_list = list(zip(best_playlist_3_images, third_best_tracks, best_playlist_3_artists, third_best_tracks_uris))
    best_playlist_2_full_list = list(zip(best_playlist_2_images, second_best_tracks, best_playlist_2_artists, second_best_tracks_uris))
    best_playlist_1_full_list = list(zip(best_playlist_1_images, first_best_tracks, best_playlist_1_artists, first_best_tracks_uris))

    best_playlists_full_list = list()
    best_playlists_full_list.append(best_playlist_1_full_list)
    best_playlists_full_list.append(best_playlist_2_full_list)
    best_playlists_full_list.append(best_playlist_3_full_list)
        
    session["best_p_list"] = best_playlists_full_list

    return render_template("playlist_showcase.html", first_best_tracks = best_playlist_1_full_list, 
        second_best_tracks = best_playlist_2_full_list, third_best_tracks = best_playlist_3_full_list)



@app.route("/callback/qplaylist", methods=["GET", "POST"])
def callback_p():

    authorization_header = session.get("a_h")

    low_features_index = range(9)
    low_feature_names = ['acousticness', 'danceability', "energy", 
    'instrumentalness', 'liveness', 'loudness', 'speechiness','tempo', 'valence']
    low_features_dict = dict(zip(low_feature_names, low_features_index)) 


    high_features_index = range(9)
    high_feature_names = ['acousticness', 'danceability', "energy", 
    'instrumentalness', 'liveness', 'loudness', 'speechiness','tempo', 'valence']
    high_features_dict = dict(zip(high_feature_names, high_features_index))

#get profile and playlist data
####################################################################################
    # Get profile data
    user_profile_api_endpoint = "{}/me".format(spotify_api_url)
    profile_response = requests.get(user_profile_api_endpoint, headers=authorization_header)
    profile_data = json.loads(profile_response.text)

    # Get user playlist data
    playlist_api_endpoint = "{}/playlists?limit=50".format(profile_data["href"])
    playlists_response = requests.get(playlist_api_endpoint, headers=authorization_header)
    playlist_data = json.loads(playlists_response.text)

    ##get user playlists info in batches of 10
    number_of_playlists = playlist_data["total"]


    if number_of_playlists % 10 > 5:
        runs = int(round(number_of_playlists/10,0)) 
    else:
        runs = int(round(number_of_playlists/10,0)) + 1


    playlist_names = []
    playlist_ids=[]
    image_list = []
    playlist_images = []   

    for i in range(runs):

        if i != list(range(runs))[-1]:
            offset = 10 * i

            playlist_api_endpoint = "{}/playlists?limit=10&offset={}".format(profile_data["href"], offset)
            playlists_response = requests.get(playlist_api_endpoint, headers=authorization_header)
            playlist_data_2 = json.loads(playlists_response.text)
            
            for n in range(10):
                current_p_name =  playlist_data_2["items"][n]["name"]
                playlist_names.append(current_p_name)

            # Combine profile and playlist data to display
            for n in range(10) :
                display_arr =  playlist_data_2["items"][n]["id"]
                playlist_ids.append(display_arr)

        if i == list(range(runs))[-1]:
            offset = number_of_playlists - (number_of_playlists % 10)

            playlist_api_endpoint = "{}/playlists?limit=10&offset={}".format(profile_data["href"], offset)
            playlists_response = requests.get(playlist_api_endpoint, headers=authorization_header)
            playlist_data_2 = json.loads(playlists_response.text)

            for n in range(len(playlist_data_2["items"])):
                current_p_name =  playlist_data_2["items"][n]["name"]
                playlist_names.append(current_p_name)

            # Combine profile and playlist data to display
            for n in range(len(playlist_data_2["items"])) :
                display_arr =  playlist_data_2["items"][n]["id"]
                playlist_ids.append(display_arr)

    ##get playlist images
    for n in range(len(playlist_ids)):
        playlist_api_endpoint = "{}/playlists/{}/images".format(spotify_api_url, playlist_ids[n])
        playlists_response = requests.get(playlist_api_endpoint, headers=authorization_header)
        playlist_images_full = json.loads(playlists_response.text)
        image_list.append(playlist_images_full)

    try:
        for n in range(len(image_list)):
            display_arr = image_list[n][0]["url"]
            playlist_images.append(display_arr)

    except IndexError:
        playlist_images =  ["/static/playlist.png"] * len(playlist_ids)
    

####################################################################################

#add a template for spotify generated user's top 50 songs playlist
####################################################################################
    top_key = "Your Top 50 Songs"
    top_value = "1"
    saved_key = "Your Liked Tracks"
    saved_value = "111"
    values = playlist_ids
    keys = playlist_names
    dictionary = dict(zip(keys, values))       
    l = []

    l.extend([list(a) for a in zip(values, playlist_images)])


    values.insert(0, saved_value)
    keys.insert(0, saved_key)
    playlist_images.insert(0, "/static/saved_tracks.png")
    values.insert(0, top_value)
    keys.insert(0, top_key)
    playlist_images.insert(0, "/static/top50.png")




    dictionary_with_images = list()
    dictionary_with_images = list(zip(keys, values, playlist_images ))    
####################################################################################
    return render_template("index.html", sorted_array=  dictionary_with_images)




@app.route("/callback/q1", methods=["GET", "POST"])
def callback_1():

##do checks for the top 50 playlists
####################################################################################
    if request.method == "POST":
        selected_playlists_ids = request.form.getlist("checkbox_my")
        selected_playlists_ids = list(selected_playlists_ids)
        #return "Done"
        
    #if no playlists selected return an error
    if not selected_playlists_ids:
        return render_template("error_page1.html")


    #check if user selected saved tracks
    saved_tracks_triggered = 0
    if any(t == "111" for t in selected_playlists_ids):
        saved_tracks_triggered = 1
        selected_playlists_ids.remove("111")
    

    ##check if user selected top 50 songs as one of the playlists
    top_tracks = 0
    if any(t == "1" for t in selected_playlists_ids):
        top_tracks = 1
        selected_playlists_ids.remove("1")
    
    session["saved_tracks_triggered"] = saved_tracks_triggered
    session["top_tracks"] = top_tracks
    session["p_ids"] = selected_playlists_ids


####################################################################################

#make objects for audio features and their icons
####################################################################################
    icons = ["/static/acoustic.png", "/static/dance.png","/static/energy.png",
        "/static/instrument.png","/static/live.png","/static/loud.png",
        "/static/speech.png","/static/tempo.png","/static/happy.png"]

    icons2 = ["/static/acoustic1.png", "/static/dance1.png","/static/energy1.png",
        "/static/instrument1.png","/static/live1.png","/static/loud1.png",
        "/static/speech1.png","/static/tempo1.png","/static/happy1.png"]
    
    low_features_index = range(9)
    low_feature_names = ['acousticness', 'danceability', "energy", 
    'instrumentalness', 'liveness', 'loudness', 'speechiness','tempo', 'valence']

    low_features_dict = dict(zip(low_feature_names, low_features_index)) 


    high_features_index = range(9)
    high_feature_names = ['acousticness', 'danceability', "energy", 
    'instrumentalness', 'liveness', 'loudness', 'speechiness','tempo', 'valence']

    low_feats_with_icons = list(zip(low_feature_names, low_features_index, icons2 ))   
    high_feats_with_icons = list(zip(high_feature_names, high_features_index, icons )) 
####################################################################################

    return render_template("feature_selection.html", low_features_dict= low_feats_with_icons,high_features_dict = high_feats_with_icons)




@app.route("/callback/playlist_showcase", methods=["GET", "POST"])
def callback_feat_sel_4():

    low_feature_names = ['acousticness', 'danceability', "energy", 
    'instrumentalness', 'liveness', 'loudness', 'speechiness','tempo', 'valence']

    high_feature_names = ['acousticness', 'danceability', "energy", 
    'instrumentalness', 'liveness', 'loudness', 'speechiness','tempo', 'valence']

    
    #get selected audio features from 
####################################################################################
    if request.method == "POST":
        selected_high_features_inds = request.form.getlist("high_features_checkbox")
        selected_low_features_inds = request.form.getlist("low_features_checkbox")

        #if no features selected return an error
        if not selected_high_features_inds and not selected_low_features_inds:
            return render_template("error_page_2.html")

        selected_high_features_inds = list(map(int, selected_high_features_inds))
        selected_low_features_inds = list(map(int, selected_low_features_inds))

        MaxFeatures = [high_feature_names[i] for i in selected_high_features_inds]
        MinFeatures = [low_feature_names[i] for i in selected_low_features_inds]
        
    user_choice_dict = {"low_features": [1], "high_features": [1]}

    final_selected_high_features = np.zeros(1)
    final_selected_low_features = np.zeros(1)

    if not MaxFeatures:
        final_selected_high_features[0] = 1
    else:
        final_selected_high_features = np.array(MaxFeatures)

    if not MinFeatures:
        final_selected_low_features[0] = 1
    else:
        final_selected_low_features = np.array(MinFeatures)


    ##if users dont select any features then return an error page
    if bool(set(selected_high_features_inds) & set(selected_low_features_inds)):
        return render_template("error_page_2.html")
####################################################################################

##get songs from the selected playlists
####################################################################################
    authorization_header = session.get("a_h")
    selected_playlists_ids = session.get("p_ids")

    current_playlist_id_list = selected_playlists_ids
    all_needed_track_ids = []
    all_needed_track_names = []
   
    for i in range(len(current_playlist_id_list)):
        current_playlist_id = current_playlist_id_list[i]

        # Get selected user playlist tracks names
        playlist_api_endpoint = "{}/playlists/{}/tracks?fields=items(track(name))".format(spotify_api_url, current_playlist_id)
        playlists_response = requests.get(playlist_api_endpoint, headers=authorization_header)
        playlist_tracks = json.loads(playlists_response.text)

        current_playlist_length = len(playlist_tracks["items"])
        current_playlists_track_names=[]
        for n in range(current_playlist_length):
            selected_playlists_track_names = list(playlist_tracks["items"][n].values())[0]
            current_playlists_track_names.append(selected_playlists_track_names)

        selected_playlists_song_names=[]
        for n in range(current_playlist_length):
            current_song_name = current_playlists_track_names[n]["name"]
            selected_playlists_song_names.append(current_song_name)

        all_needed_track_names.append(selected_playlists_song_names)


        # Get selected user playlist tracks ids
        playlist_api_endpoint = "{}/playlists/{}/tracks?fields=items(track(id))".format(spotify_api_url, current_playlist_id)
        playlists_response = requests.get(playlist_api_endpoint, headers=authorization_header)
        playlist_tracks = json.loads(playlists_response.text)

        current_playlist_length = len(playlist_tracks["items"])
        current_playlists_track_ids = []
        for n in range(current_playlist_length):
            selected_playlists_track_id = list(playlist_tracks["items"][n].values())[0]
            current_playlists_track_ids.append(selected_playlists_track_id)

        selected_playlists_song_ids = []
        for n in range(current_playlist_length):
            current_song_id = current_playlists_track_ids[n]["id"]
            selected_playlists_song_ids.append(current_song_id)

        all_needed_track_ids.append(selected_playlists_song_ids)
    

    ##get users saved tracks info if triggered 
    saved_tracks_triggered = session.get("saved_tracks_triggered")
    if saved_tracks_triggered == 1:

        playlist_api_endpoint = "{}/me/tracks?limit=10&offset=0".format(spotify_api_url)
        playlists_response = requests.get(playlist_api_endpoint, headers=authorization_header)
        user_saved_tracks = json.loads(playlists_response.text)

        number_of_saved_songs = user_saved_tracks["total"]

        if number_of_saved_songs % 10 > 5:
            runs = int(round(number_of_saved_songs/10,0)) 
        else:
            runs = int(round(number_of_saved_songs/10,0)) + 1

        saved_track_names = []
        saved_track_id = []

        for i in range(runs):

            if i != list(range(runs))[-1]:
                offset = 10 * i

                playlist_api_endpoint = "{}/me/tracks?limit=10&offset={}".format(spotify_api_url, offset)
                playlists_response = requests.get(playlist_api_endpoint, headers=authorization_header)
                user_saved_tracks = json.loads(playlists_response.text)
            
                for n in range(10):
                    current_t_name = user_saved_tracks["items"][n]["track"]["name"]
                    saved_track_names.append(current_t_name)

                # Combine profile and playlist data to display
                for n in range(10) :
                    current_t_id =  user_saved_tracks["items"][n]["track"]["id"]
                    saved_track_id.append(current_t_id)

            if i == list(range(runs))[-1]:
                offset = number_of_saved_songs - (number_of_saved_songs % 10)

                playlist_api_endpoint = "{}/me/tracks?limit=10&offset={}".format(spotify_api_url, offset)
                playlists_response = requests.get(playlist_api_endpoint, headers=authorization_header)
                user_saved_tracks = json.loads(playlists_response.text)

                for n in range(len(user_saved_tracks["items"])):
                    current_t_name =  user_saved_tracks["items"][n]["track"]["name"]
                    saved_track_names.append(current_t_name)

                # Combine profile and playlist data to display
                for n in range(len(user_saved_tracks["items"])) :
                    curent_t_id =  user_saved_tracks["items"][n]["track"]["id"]
                    saved_track_id.append(curent_t_id)

        all_needed_track_names.append(saved_track_names)
        all_needed_track_ids.append(saved_track_id)



    ##get users top 50 tracks playlist (generated by spotify) if triggered:
    top_tracks = session.get("top_tracks")
    if top_tracks == 1:

        playlist_api_endpoint = "{}/me/top/tracks?time_range=medium_term&limit=100".format(spotify_api_url)
        playlists_response = requests.get(playlist_api_endpoint, headers=authorization_header)
        top_50_tracks = json.loads(playlists_response.text)

        top50_length = len(top_50_tracks["items"])

        top_50_playlist_track_names=[]
        for n in range(top50_length):
            top50_tracks_names = top_50_tracks["items"][n]["name"]
            top_50_playlist_track_names.append(top50_tracks_names)
        all_needed_track_names.append(top_50_playlist_track_names)
     

        top_50_playlist_track_IDs=[]
        for n in range(top50_length):
            top50_tracks_ids = top_50_tracks["items"][n]["id"]
            top_50_playlist_track_IDs.append(top50_tracks_ids)
        all_needed_track_ids.append(top_50_playlist_track_IDs)

 
        
####################################################################################
##get features from the selected tracks
####################################################################################
    track_features_list = []

    for d in range(len(all_needed_track_ids)):
        for i in range(len(all_needed_track_ids[d])):
            current_track_id = all_needed_track_ids[d][i]
          
            playlist_api_endpoint = "{}/audio-features/{}".format(spotify_api_url, current_track_id)
            playlists_response = requests.get(playlist_api_endpoint, headers=authorization_header)
            track_features = json.loads(playlists_response.text)

            track_features_list.append(track_features)

    all_needed_track_names_flat = [item for sublist in all_needed_track_names for item in sublist]
    number_of_tracks_chosen = len(all_needed_track_names_flat)

    if number_of_tracks_chosen < 30:
       return render_template("error_page1.html")
   
    total_features_flat = np.zeros(0)
    condition = "none"
    if(final_selected_low_features[0] != 1. and final_selected_high_features[0] != 1.):
        total_features_flat = np.concatenate((final_selected_low_features, final_selected_high_features), axis=None)
        condition = "both"
    elif(final_selected_low_features[0] == 1 and final_selected_high_features[0] != 1):
        total_features_flat = final_selected_high_features.copy()
        condition = "max"
    elif(final_selected_low_features[0] != 1 and final_selected_high_features[0] == 1):
        total_features_flat = final_selected_low_features.copy()
        condition = "min"

    ##make a the DF with track info including audio features.
    track_features_DF = pd.DataFrame(track_features_list)


    track_features_DF['track_names'] = all_needed_track_names_flat
    track_features_DF_filtered_for_clustering = track_features_DF[total_features_flat]

    track_features_DF_filtered_for_clustering_scaled = sk.preprocessing.scale(track_features_DF_filtered_for_clustering)
    track_features_DF_filtered_for_clustering_scaled = pd.DataFrame(track_features_DF_filtered_for_clustering_scaled)
    
    track_features_DF_filtered_for_clustering_scaled = track_features_DF_filtered_for_clustering_scaled.drop_duplicates(keep="first")
    track_features_DF_filtered_for_clustering_scaled = track_features_DF_filtered_for_clustering_scaled.replace([np.inf, -np.inf], np.nan)
    track_features_DF_ready_for_clustering = track_features_DF_filtered_for_clustering_scaled.dropna()
####################################################################################



    ##run the clusterfy Kmeans function on the data and save the playlist/cluster info
####################################################################################
    first_best_pst, second_best_pst, third_best_pst = clusterfy_function(track_features_DF,track_features_DF_ready_for_clustering,final_selected_low_features, final_selected_high_features, condition = condition)

    #output playlist track names
    first_best_tracks = first_best_pst["track_names"]
    second_best_tracks = second_best_pst["track_names"]
    third_best_tracks = third_best_pst["track_names"]
    #output playlist track uris
    first_best_tracks_uris = list(first_best_pst["uri"])
    second_best_tracks_uris = list(second_best_pst["uri"])
    third_best_tracks_uris = list(third_best_pst["uri"])

    best_playlists_list = list()
    best_playlists_list.append(first_best_tracks)
    best_playlists_list.append(second_best_tracks)
    best_playlists_list.append(third_best_tracks)

    best_playlists_uris_list = list()
    best_playlists_uris_list.append(first_best_tracks_uris)
    best_playlists_uris_list.append(second_best_tracks_uris)
    best_playlists_uris_list.append(third_best_tracks_uris)

    access_token = session.get("a_t")
    sp = spotipy.Spotify(auth=access_token) 

    ids_best_playlist_1 = [i.split('track:', 1)[1] for i in first_best_tracks_uris]
    ids_best_playlist_2 = [i.split('track:', 1)[1] for i in second_best_tracks_uris]
    ids_best_playlist_3 = [i.split('track:', 1)[1] for i in third_best_tracks_uris]

    #use the get_track_info function to get artist names and album images of tracks from the created playlist
    best_playlist_1_artists, best_playlist_1_images = get_track_info(ids_best_playlist_1, access_token)
    best_playlist_2_artists, best_playlist_2_images = get_track_info(ids_best_playlist_2, access_token)
    best_playlist_3_artists, best_playlist_3_images = get_track_info(ids_best_playlist_3, access_token)    

    best_playlist_3_full_list = list(zip(best_playlist_3_images, third_best_tracks, best_playlist_3_artists, third_best_tracks_uris))
    best_playlist_2_full_list = list(zip(best_playlist_2_images, second_best_tracks, best_playlist_2_artists, second_best_tracks_uris))
    best_playlist_1_full_list = list(zip(best_playlist_1_images, first_best_tracks, best_playlist_1_artists, first_best_tracks_uris))

    best_playlists_full_list = list()
    best_playlists_full_list.append(best_playlist_1_full_list)
    best_playlists_full_list.append(best_playlist_2_full_list)
    best_playlists_full_list.append(best_playlist_3_full_list)
        
    session["best_p_list"] = best_playlists_full_list
####################################################################################

    return render_template("playlist_showcase.html", first_best_tracks = best_playlist_1_full_list, 
        second_best_tracks = best_playlist_2_full_list, third_best_tracks = best_playlist_3_full_list)



@app.route("/callback/playlist_upload_page", methods=["GET", "POST"])
def playlist_upload():
    ##this page showcases the created playlists by the clusterfy kmeans function
    ##see which playlist user selected
    if request.method == 'POST':
        if request.form.get('upload_playlist_1_button') == "Upload Playlist":
            playlist_selected_for_upload = 1 
        elif request.form.get('upload_playlist_2_button') == "Upload Playlist":
            playlist_selected_for_upload = 0
        elif request.form.get('upload_playlist_3_button') == "Upload Playlist":
            playlist_selected_for_upload = 2

    session["playlist_index"] = playlist_selected_for_upload

    best_playlists_full_list = session.get("best_p_list")
    best_playlist_1_full_list = best_playlists_full_list[0]
    best_playlist_2_full_list = best_playlists_full_list[1]
    best_playlist_3_full_list = best_playlists_full_list[2]

    return render_template("name_new_playlist.html", first_best_tracks = best_playlist_1_full_list, 
        second_best_tracks = best_playlist_2_full_list, third_best_tracks = best_playlist_3_full_list)

@app.route("/callback/playlist_create_page", methods=["GET", "POST"])
def playlist_create():
    access_token = session.get("a_t")
    sp = spotipy.Spotify(auth=access_token)

    #get the name user wants for their selected clusterfy playlist
    new_playlist_name = request.form["Name Your New Playlist"]
    playlist_selected_for_upload = session.get("playlist_index")

    #organise the clusterfy playlists info
    best_playlists_full_list = session.get("best_p_list")
    best_playlist_1_full_list = best_playlists_full_list[0]
    best_playlist_2_full_list = best_playlists_full_list[1]
    best_playlist_3_full_list = best_playlists_full_list[2]

    p1_uris = [i[3] for i in best_playlist_1_full_list]
    p2_uris = [i[3] for i in best_playlist_2_full_list]
    p3_uris = [i[3] for i in best_playlist_3_full_list]

    best_playlists_uris_FINAL = list()
    best_playlists_uris_FINAL.append(p1_uris)
    best_playlists_uris_FINAL.append(p2_uris)
    best_playlists_uris_FINAL.append(p3_uris)
    
    #get user data and the id of the newly made (for now empty) clusterfy playlist
    user_all_data = sp.current_user()
    USER_ID = user_all_data["id"]

    playlist_all_data = sp.user_playlist_create(USER_ID, str(new_playlist_name))
    new_playlist_id = playlist_all_data["id"]

    #upload the needed tracks into the empty playlist using track uris
    selected_playlist_song_uris = best_playlists_uris_FINAL[playlist_selected_for_upload]

    if len(selected_playlist_song_uris) < 98:
        sp.user_playlist_add_tracks(USER_ID, new_playlist_id, selected_playlist_song_uris)
    else:
        selected_songs_upload1 = selected_playlist_song_uris[0:98]
        selected_songs_upload2 = selected_playlist_song_uris[98:]

        sp.user_playlist_add_tracks(USER_ID, new_playlist_id, selected_songs_upload1)
        sp.user_playlist_add_tracks(USER_ID, new_playlist_id, selected_songs_upload2)


    return render_template("final_page.html", first_best_tracks = best_playlist_1_full_list, 
        second_best_tracks = best_playlist_2_full_list, third_best_tracks = best_playlist_3_full_list)


if __name__ == "__main__":
    app.run(debug=True, port=port)
    
