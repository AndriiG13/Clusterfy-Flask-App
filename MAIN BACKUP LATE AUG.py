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




# Authentication Steps, paramaters, and responses are defined at https://developer.spotify.com/web-api/authorization-guide/
# Visit this url to see all the steps, parameters, and expected response.


app = Flask(__name__)

SESSION_TYPE = 'redis'
app.config.from_object(__name__)
Session(app)

def randomword(length):
   letters = string.ascii_lowercase
   return ''.join(random.choice(letters) for i in range(length))

secret_user = randomword(20)

app.config['SECRET_KEY'] = secret_user


#  Client Keys
CLIENT_ID = "d5ec308d7b9749b5b49c3e4da6ef4da2"
CLIENT_SECRET = "0e137083f0b149e8afa2eaa57f59fb94"

# Spotify URLS
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com"
API_VERSION = "v1"
SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)

# Server-side Parameters
CLIENT_SIDE_URL = "http://127.0.0.1"
PORT = 8080
REDIRECT_URI = "{}:{}/callback/q".format(CLIENT_SIDE_URL, PORT)
SCOPE = "playlist-modify-public playlist-modify-private user-top-read user-library-read playlist-read-private playlist-read-collaborative"
STATE = ""
SHOW_DIALOG_bool = True
SHOW_DIALOG_str = str(SHOW_DIALOG_bool).lower()

auth_query_parameters = {
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "scope": SCOPE,
    # "state": STATE,
    # "show_dialog": SHOW_DIALOG_str,
    "client_id": CLIENT_ID


}


@app.route("/", methods=["GET", "POST"])
def intro():
    # Auth Step 1: Authorization

    
    return render_template("first_page.html")



@app.route("/auth", methods=["GET", "POST"])
def index():
    # Auth Step 1: Authorization
    url_args = "&".join(["{}={}".format(key, quote(val)) for key, val in auth_query_parameters.items()])
    auth_url = "{}/?{}".format(SPOTIFY_AUTH_URL, url_args)
    print("AUTH URL")
    print(auth_url)
    return redirect(auth_url)

@app.route("/callback/q", methods=["GET", "POST"])
def callback():
    ############################################################
    # Auth Step 4: Requests refresh and access tokens
    auth_token = request.args['code']
    code_payload = {
        "grant_type": "authorization_code",
        "code": str(auth_token),
        "redirect_uri": REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    }
    post_request = requests.post(SPOTIFY_TOKEN_URL, data=code_payload)
############
    # Auth Step 5: Tokens are Returned to Application
    response_data = json.loads(post_request.text)
    access_token = response_data["access_token"]
    #access_token1 = access_token
    refresh_token = response_data["refresh_token"]
    token_type = response_data["token_type"]
    expires_in = response_data["expires_in"]

    session["a_t"] = access_token
    

    # Auth Step 6: Use the access token to access Spotify API
    authorization_header = {"Authorization": "Bearer {}".format(access_token)}

    session["a_h"] = authorization_header


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
    #save auth token for later use
    
    #access_token_dict[secret_user]["acc_t"] = access_token
    # Get profile data
    user_profile_api_endpoint = "{}/me".format(SPOTIFY_API_URL)
    profile_response = requests.get(user_profile_api_endpoint, headers=authorization_header)
    profile_data = json.loads(profile_response.text)


    # Get user playlist data
    playlist_api_endpoint = "{}/playlists?limit=50".format(profile_data["href"])
    playlists_response = requests.get(playlist_api_endpoint, headers=authorization_header)
    playlist_data = json.loads(playlists_response.text)


    t = playlist_data["total"]
    t2 = playlist_data["total"]
    if t > 50:
        playlist_api_endpoint = "{}/playlists?limit=50&offset=50".format(profile_data["href"])
        playlists_response = requests.get(playlist_api_endpoint, headers=authorization_header)
        playlist_dat2 = json.loads(playlists_response.text)

   

    
####################################################################################
   
   ## save the total playists number, then save each playlist name
   ########################################################################
    
 
    if t2 > 50:
        t = 50

    if t2 == 51:
        t = 50

        print("TOTAL")
    print(t2)
    if t2 > 100:
        t2 = 100



    minus_t = 50

    if t == 51:
        minus_t = 51

    xx=[]
    # Combine profile and playlist data to display
    for n in range(t) :
     
        display_arr =  playlist_data["items"][n]["name"]
        xx.append(display_arr)


    
    playlist_ids=[]
    # Combine profile and playlist data to display
    for n in range(t) :
        display_arr =  playlist_data["items"][n]["id"]
        playlist_ids.append(display_arr)

    

    xx_name2 = []
    if t2 > minus_t:
        for n in range(t2-50) :
          
            display_arr =  playlist_dat2["items"][n]["name"]
            xx_name2.append(display_arr)

 

        playlist_ids2=[]
    # Combine profile and playlist data to display
        for n in range(t2-50) :
    
            display_arr =  playlist_dat2["items"][n]["id"]
            playlist_ids2.append(display_arr)
       



###THIS SHOWS THE CHECBKX FOR PLAYLISTS SELECTION
##make it into a dixtionary and pass values as the range of all ps and
#keys as the name of the playlist
############################################################

    top_key = "Your Top 50 Songs"
    top_value = "1"

    

    if t2 > 50:
        playlist_ids = playlist_ids + playlist_ids2
        xx = xx + xx_name2


 

  
    values = playlist_ids
    keys = xx
    dictionary = dict(zip(keys, values))       

    if t2 <= 100:
        image_list = []
        for n in range(t2):

            playlist_api_endpoint = "{}/playlists/{}/images".format(SPOTIFY_API_URL, playlist_ids[n])
            playlists_response = requests.get(playlist_api_endpoint, headers=authorization_header)
            playlist_images_full = json.loads(playlists_response.text)
            image_list.append(playlist_images_full)

    elif t2 > 100:
        image_list = []
        t2 = 100
        for n in range(t2):

            playlist_api_endpoint = "{}/playlists/{}/images".format(SPOTIFY_API_URL, playlist_ids[n])
            playlists_response = requests.get(playlist_api_endpoint, headers=authorization_header)
            playlist_images_full = json.loads(playlists_response.text)
            image_list.append(playlist_images_full)


    if t2 <= 100:
        playlist_images = []   
        for n in range(t2) :
      
            display_arr =  image_list[n][0]["url"]
            playlist_images.append(display_arr)

    if t2 > 100:
        t2 = 100
        playlist_images = []   
        for n in range(t2) :
      
            display_arr =  image_list[n][0]["url"]
            playlist_images.append(display_arr)



    l = []
    l.extend([list(a) for a in zip(values, playlist_images)])
   


    values.insert(0, top_value)
    keys.insert(0, top_key)
    playlist_images.insert(0, "/static/top50.png")


    
    dictionary_with_images = list()
    dictionary_with_images = list(zip(keys, values, playlist_images ))    





    return render_template("index.html", sorted_array=  dictionary_with_images)

    #display_arr = [profile_data] + playlist_data["items"]
    #return render_template("index.html", sorted_array=display_arr)
############################################################


@app.route("/callback/q1", methods=["GET", "POST"])
def callback_1():

##GET PLAYLIST IDS
############################################################
    if request.method == "POST":
        selected_playlists_ids = request.form.getlist("checkbox_my")
        selected_playlists_ids = list(selected_playlists_ids)
        #return "Done"
        
   
    #subset the IDS of ONLY selected PLAYLISTS

    if not selected_playlists_ids:
        return render_template("error_page1.html")

    top_tracks = 0

    if any(t == "1" for t in selected_playlists_ids):
        top_tracks = 1
        selected_playlists_ids = selected_playlists_ids[1:]
    
    

    session["top_tracks"] = top_tracks
    session["p_ids"] = selected_playlists_ids



############################################################

##GET THE SONGS FROM SELECTED PLAYLISTS
############################################################
   
    number_of_songs2 = ["Suggested","10","15","20","35","40","45","50"]
    number_of_songs = [5,10,15,20,35,40,45,50]

    suggested_number_of_songs = 5
    number_of_songs_dict = dict(zip(number_of_songs2, number_of_songs))
    number_of_songs_dict["Suggested"] = suggested_number_of_songs


    icons = ["/static/acoustic.png", "/static/dance.png","/static/energy.png",
        "/static/instrument.png","/static/live.png","/static/loud.png",
        "/static/speech.png","/static/tempo.png","/static/happy.png"]

    icons2 = ["/static/acoustic1.png", "/static/dance1.png","/static/energy1.png",
        "/static/instrument1.png","/static/live1.png","/static/loud1.png",
        "/static/speech1.png","/static/tempo1.png","/static/happy1.png"]

    #l = []
    #l.extend([list(a) for a in zip(high_features_index, icons)])

    
    low_features_index = range(9)
    low_feature_names = ['acousticness', 'danceability', "energy", 
    'instrumentalness', 'liveness', 'loudness', 'speechiness','tempo', 'valence']

    low_features_dict = dict(zip(low_feature_names, low_features_index)) 


    high_features_index = range(9)
    high_feature_names = ['acousticness', 'danceability', "energy", 
    'instrumentalness', 'liveness', 'loudness', 'speechiness','tempo', 'valence']

    low_feats_with_icons = list(zip(low_feature_names, low_features_index, icons2 ))   
    high_feats_with_icons = list(zip(high_feature_names, high_features_index, icons )) 
  

   #temp_song = list(playlist_tracks["items"][0].values())[0]
 

    return render_template("feature_selection.html", low_features_dict= low_feats_with_icons,high_features_dict = high_feats_with_icons)
#https://api.spotify.com/v1/users/dtj7fdsb05eq0rswpflu3su6z/playlists/1o6UfTrHCgJTuMXgPSPMkl/tracks?fields=item(track(name))
#https://api.spotify.com/v1/playlists/1o6UfTrHCgJTuMXgPSPMkl/tracks?fields=item(track(name))



@app.route("/callback/playlist_showcase", methods=["GET", "POST"])
def callback_feat_sel_4():

    low_feature_names = ['acousticness', 'danceability', "energy", 
    'instrumentalness', 'liveness', 'loudness', 'speechiness','tempo', 'valence']

    high_feature_names = ['acousticness', 'danceability', "energy", 
    'instrumentalness', 'liveness', 'loudness', 'speechiness','tempo', 'valence']

    if request.method == "POST":
        selected_high_features_inds = request.form.getlist("high_features_checkbox")
        selected_low_features_inds = request.form.getlist("low_features_checkbox")

        if not selected_high_features_inds and not selected_low_features_inds:
            return render_template("error_page_2.html")

        selected_high_features_inds = list(map(int, selected_high_features_inds))
        selected_low_features_inds = list(map(int, selected_low_features_inds))
        


        T1 = [high_feature_names[i] for i in selected_high_features_inds]
        T2 = [low_feature_names[i] for i in selected_low_features_inds]
        
    user_choice_dict = {"low_features": [1], "high_features": [1], "number_of_songs": [1]}


    if not T1:
        user_choice_dict["high_features"] = [1]
    else:
        user_choice_dict["high_features"] = T1

    if not T2:
        user_choice_dict["low_features"] = [1]
    else:
        user_choice_dict["low_features"] = T2


    if bool(set(selected_high_features_inds) & set(selected_low_features_inds)):
        return render_template("error_page_2.html")
         


##GET THE SONGS FROM SELECTED PLAYLISTS
############################################################
    authorization_header = session.get("a_h")

    selected_playlists_ids = session.get("p_ids")


    current_playlist_id_list = selected_playlists_ids
    all_needed_track_names = []
    for i in range(len(current_playlist_id_list)):
        current_playlist_id = current_playlist_id_list[i]

    # Get user playlist data
        playlist_api_endpoint = "{}/playlists/{}/tracks?fields=items(track(name))".format(SPOTIFY_API_URL, current_playlist_id)
        playlists_response = requests.get(playlist_api_endpoint, headers=authorization_header)
        playlist_tracks = json.loads(playlists_response.text)
    
        current_playlist_length = len(playlist_tracks["items"])
        xx3=[]
        for n in range(current_playlist_length):
            selected_playlists_ids = list(playlist_tracks["items"][n].values())[0]
            xx3.append(selected_playlists_ids)

        #print(xx3)

        selected_playlists_song_names=[]
        for n in range(current_playlist_length):
            current_song_name = xx3[n]["name"]
            selected_playlists_song_names.append(current_song_name)

        all_needed_track_names.append(selected_playlists_song_names)




    playlist_api_endpoint = "{}/me/top/tracks?time_range=medium_term&limit=100".format(SPOTIFY_API_URL)
    playlists_response = requests.get(playlist_api_endpoint, headers=authorization_header)
    top_100_tracks = json.loads(playlists_response.text)

    top100_length = len(top_100_tracks["items"])
    xx100=[]
    for n in range(top100_length):
        top100_tracks_names = top_100_tracks["items"][n]["name"]
        xx100.append(top100_tracks_names)

    top_tracks = session.get("top_tracks")
    if top_tracks == 1:
        all_needed_track_names.append(xx100)

 

    #print(all_needed_track_names)


    xx101=[]
    for n in range(top100_length):
        top100_tracks_names = top_100_tracks["items"][n]["id"]
        xx101.append(top100_tracks_names)



    all_needed_track_ids = []
    for i in range(len(current_playlist_id_list)):
        current_playlist_id = current_playlist_id_list[i]

    # Get user playlist data
        playlist_api_endpoint = "{}/playlists/{}/tracks?fields=items(track(id))".format(SPOTIFY_API_URL, current_playlist_id)
        playlists_response = requests.get(playlist_api_endpoint, headers=authorization_header)
        playlist_tracks = json.loads(playlists_response.text)
    
        current_playlist_length = len(playlist_tracks["items"])
        xx3=[]
        for n in range(current_playlist_length):
            selected_playlists_ids = list(playlist_tracks["items"][n].values())[0]
            xx3.append(selected_playlists_ids)

        

        selected_playlists_song_ids=[]
        for n in range(current_playlist_length):
            current_song_id = xx3[n]["id"]
            selected_playlists_song_ids.append(current_song_id)

        all_needed_track_ids.append(selected_playlists_song_ids)

    
    if top_tracks == 1:
        all_needed_track_ids.append(xx101)

        
   
############################################################



############################################################
    track_features_list = []
    track_features_list_complete = []

    #print(range(len(all_needed_track_ids)))

    for d in range(len(all_needed_track_ids)):

        for i in range(len(all_needed_track_ids[d])):
            current_track_id = all_needed_track_ids[d][i]
            #print(current_track_id)
            playlist_api_endpoint = "{}/audio-features/{}".format(SPOTIFY_API_URL, current_track_id)
            playlists_response = requests.get(playlist_api_endpoint, headers=authorization_header)
            track_features = json.loads(playlists_response.text)

            track_features_list.append(track_features)

        track_features_list_complete.append(track_features_list)

    #print(track_features_list_complete)










    all_needed_track_names_flat = [item for sublist in all_needed_track_names for item in sublist]
    
    
  

    #print(flat_list)
    track_features_DF = pd.DataFrame(track_features_list, index = all_needed_track_names_flat)
    

    track_features_DF = track_features_DF[['id', 'uri', 'acousticness', 'danceability', "energy", 
    'instrumentalness', 'liveness', 'loudness', 'speechiness','tempo', 'valence' ]]

    number_of_tracks_chosen = len(all_needed_track_names_flat)


    if number_of_tracks_chosen < 30:
       return render_template("error_page1.html")
   

        
        #print(all_needed_track_names_flat)
    


    future_cond = 1

     #del high_features_dict[selected_low_features_inds
    if request.method == "POST":
        selected_number_of_songs = request.form.get("generate_playlist_button")
    
        final_selected_low_features = user_choice_dict["low_features"]
       
        final_selected_high_features = user_choice_dict["high_features"]
 


    if(str(final_selected_low_features[0]) != "1" and str(final_selected_high_features[0]) != "1"):
        total_features = [final_selected_low_features, final_selected_high_features]
        total_features_flat = [val for sublist in total_features for val in sublist]
        future_cond = 1
    elif(str(final_selected_low_features[0]) == "1" and str(final_selected_high_features[0]) != "1"):
        total_features_flat = list(final_selected_high_features)
        future_cond = 2
    elif(str(final_selected_low_features[0]) != "1" and str(final_selected_high_features[0]) == "1"):
        total_features_flat = list(final_selected_low_features)
        future_cond = 3


    #print(total_features_flat)
        #total_features_flat = [val for sublist in total_features for val in sublist]
        #print(total_features_flat)
 

    #print(selected_playlists_ids)

    #print(xx2)
############################################################


    track_features_DF = pd.DataFrame(track_features_list)
    track_features_DF['track_names'] = all_needed_track_names_flat
        
       # print(track_features_DF.columns)
        #track_features_DF_ready_to_filter = track_features_DF.drop_duplicates(subset=["id"], keep="first")
        #print(track_features_DF_ready_to_filter)
        #print(track_features_DF_ready_to_filter)
       # print(track_features_DF.columns)
       # print(total_features)

    track_features_DF_filtered_for_clustering = track_features_DF[total_features_flat]
        #print(track_features_DF_ready_to_filter)
    original_df_columns = track_features_DF_filtered_for_clustering.columns
        #print(original_df_columns)

        
    all_needed_track_length = {"length": 1}

    all_selected_tracks_length = all_needed_track_length["length"]

    number_of_clusters = track_features_DF.shape[0] / 10
    number_of_clusters = round(number_of_clusters)

    if (number_of_clusters > 6):
        number_of_clusters = 6

        #np.interp(a, (a.min(), a.max()), (0, +100))


    print("SET CLUSTER = " + str(number_of_clusters))
        
    track_features_DF_filtered_for_clustering_scaled = sk.preprocessing.scale(track_features_DF_filtered_for_clustering)
    track_features_DF_filtered_for_clustering_scaled = pd.DataFrame(track_features_DF_filtered_for_clustering_scaled)
    

    scaled_full_tracks_for_later = pd.DataFrame(track_features_DF_filtered_for_clustering_scaled)
    scaler = MinMaxScaler(feature_range = (0,100))
    scaler.fit(scaled_full_tracks_for_later)
    scaled_full_tracks_for_later = scaler.transform(scaled_full_tracks_for_later)
    scaled_full_tracks_for_later = pd.DataFrame(scaled_full_tracks_for_later)


    scaled_full_tracks_for_later = scaled_full_tracks_for_later.drop_duplicates(keep="first")
    scaled_full_tracks_for_later = scaled_full_tracks_for_later.replace([np.inf, -np.inf], np.nan)
    
    track_features_DF_filtered_for_clustering_scaled = track_features_DF_filtered_for_clustering_scaled.drop_duplicates(keep="first")
    track_features_DF_filtered_for_clustering_scaled = track_features_DF_filtered_for_clustering_scaled.replace([np.inf, -np.inf], np.nan)
    


    scaled_full_tracks_for_later = pd.DataFrame(track_features_DF_filtered_for_clustering_scaled)
    

    #scaler = MinMaxScaler(feature_range = (0,100))
   # scaler.fit(scaled_full_tracks_for_later)
    #scaled_full_tracks_for_later = scaler.transform(scaled_full_tracks_for_later)
    #scaled_full_tracks_for_later = pd.DataFrame(scaled_full_tracks_for_later)
    


       # track_features_DF_filtered_for_clustering_scaled["track_name"] = all_needed_track_names_flat
        #print(track_features_DF_filtered_for_clustering_scaled.set_index("track_names", drop = True))
    track_features_DF_filtered_for_clustering_scaled_cleaned = track_features_DF_filtered_for_clustering_scaled.dropna()
        



       # print(track_features_DF_filtered_for_clustering_scaled_cleaned)

    total_features_flat_1 = list(total_features_flat)
    total_features_flat.append("clusters")

    playlist_best_cluster_from_the_loop = []
    playlist_max_from_the_loop = []
    datalist = list()
        
    if(future_cond == 1):
        for i in range(50):
            random_state_value = randrange(3000)    
           #     print(number_of_clusters)
            number_of_clusters_1 = randint(number_of_clusters-4,number_of_clusters+4)
            if(number_of_clusters_1 < 2):
                number_of_clusters_1=2
            elif(track_features_DF.shape[0] / number_of_clusters_1 < 10):
                number_of_clusters_1 = number_of_clusters

               # print("RANDOMCLUSTER = "+ str(number_of_clusters_1))
        #print(track_features_DF_filtered_for_clustering_scaled_cleaned)
            kmeans_obj = KMeans(n_clusters=number_of_clusters_1, init='k-means++', 
            max_iter=100, n_init=15, verbose=0, random_state=random_state_value)
       #print(kmeans_obj)
            kmeans_obj.fit(track_features_DF_filtered_for_clustering_scaled_cleaned)
        #print(kmeans_obj)
            kmeans_output = kmeans_obj.labels_

        
            cluster_sizes = Counter(kmeans_output)
       
            counter_np  = np.fromiter(cluster_sizes.values(), dtype=float)
            counter_np_key  = np.fromiter(cluster_sizes.keys(), dtype=int)

            big_clusters = counter_np_key[counter_np > 10]

            track_features_DF_filtered_for_clustering_scaled_cleaned["clusters"] = kmeans_output
        
            big_clusters_list = list(big_clusters)
            big_clusters_list_str = map(str, big_clusters_list)
        

            track_features_DF_only_good_clusters = track_features_DF_filtered_for_clustering_scaled_cleaned.query('clusters in @big_clusters_list_str')
            track_features_DF_only_good_clusters.columns = total_features_flat


       # print(track_features_DF_only_good_clusters)
       
   
            df_low_features = track_features_DF_only_good_clusters[list(final_selected_low_features)]
            low_means = (df_low_features.mean(axis = 1))

            df_high_features = track_features_DF_only_good_clusters[list(final_selected_high_features)]
            high_means = (df_high_features.mean(axis = 1))
            
            track_features_DF_only_good_clusters["low_means"] = low_means
            track_features_DF_only_good_clusters["high_means"] = high_means

            #print(track_features_DF_only_good_clusters)
            playlist_score_df =  (track_features_DF_only_good_clusters
                .assign(playlist_score = high_means - low_means)
                .groupby("clusters")
                .agg(['mean']))

           # print(playlist_score_df)
            

            playlist_score_df_only_score =  playlist_score_df["playlist_score"]
            max_index = playlist_score_df_only_score.idxmax(axis = 0)
            max_index_1 = playlist_score_df_only_score.max(axis = 0)
            playlist_max_from_the_loop.append(max_index_1[0])

           # print(playlist_score_df_only_score)
           # print(max_index[0])

            best_cluster_df = track_features_DF_only_good_clusters[track_features_DF_only_good_clusters["clusters"] == max_index[0]]
          

            #print(best_cluster_df)
           # print(best_cluster_df)
            best_cluster_df_2 = track_features_DF[track_features_DF.index.isin(best_cluster_df.index)]
            best_cluster_df_2["iteration"] = i
           # print(best_cluster_df_2)
           # print(best_cluset_df_2)
            playlist_best_cluster_from_the_loop.append(max_index[0])
            datalist.append(best_cluster_df_2)
            #print(best_cluster_df_2)
         
            

        #print(playlist_best_cluster_from_the_loop)
        #print(playlist_max_from_the_loop)
        #print(datalist)


    elif(future_cond == 2):
        for i in range(50):
                random_state_value = randrange(3000)    
           #     print(number_of_clusters)

                number_of_clusters_1 = randint(number_of_clusters-4,number_of_clusters+4)
                if(number_of_clusters_1 < 2):
                    number_of_clusters_1=2
                elif(track_features_DF.shape[0] / number_of_clusters_1 < 10):
                    number_of_clusters_1 = number_of_clusters

               # print("RANDOMCLUSTER = "+ str(number_of_clusters_1))
        #print(track_features_DF_filtered_for_clustering_scaled_cleaned)
                kmeans_obj = KMeans(n_clusters=number_of_clusters_1, init='k-means++', 
                max_iter=100, n_init=15, verbose=0, random_state=random_state_value)
       #print(kmeans_obj)
                kmeans_obj.fit(track_features_DF_filtered_for_clustering_scaled_cleaned)
        #print(kmeans_obj)
                kmeans_output = kmeans_obj.labels_

        
                cluster_sizes = Counter(kmeans_output)
       
                counter_np  = np.fromiter(cluster_sizes.values(), dtype=float)
                counter_np_key  = np.fromiter(cluster_sizes.keys(), dtype=int)

                big_clusters = counter_np_key[counter_np > 10]

                track_features_DF_filtered_for_clustering_scaled_cleaned["clusters"] = kmeans_output
        
                big_clusters_list = list(big_clusters)
                big_clusters_list_str = map(str, big_clusters_list)
        

                track_features_DF_only_good_clusters = track_features_DF_filtered_for_clustering_scaled_cleaned.query('clusters in @big_clusters_list_str')
                track_features_DF_only_good_clusters.columns = total_features_flat


       # print(track_features_DF_only_good_clusters)
       
   
                #df_low_features = track_features_DF_only_good_clusters[list(final_selected_low_features)]
                #low_means = (df_low_features.mean(axis = 1))
               # print("TRACK FEATURES FULL")
                #print(track_features_DF_only_good_clusters)
                df_high_features = track_features_DF_only_good_clusters[final_selected_high_features]
               # print("final_selected_high_features")
               # print(final_selected_high_features)
               # print("DF_HIGH_FEATURES")
               # print(df_high_features)
                high_means = (df_high_features.mean(axis = 1))
               # print("HIGH MEANS") 
                #print(high_means)
                #track_features_DF_only_good_clusters["low_means"] = low_means
                track_features_DF_only_good_clusters["high_means"] = high_means
               # print("TRACK FEATS HIGH MEANS MEANS") 
               # print(track_features_DF_only_good_clusters)

            #print(track_features_DF_only_good_clusters)
                playlist_score_df =  (track_features_DF_only_good_clusters
                    .assign(playlist_score = high_means)
                    .groupby("clusters")
                    .agg(['mean']))

               # print("PLAYLIST_DF")
               # print(playlist_score_df)

                playlist_score_df_only_score = playlist_score_df["playlist_score"]
                max_index = playlist_score_df_only_score.idxmax(axis = 0)
                #print("MAX INDEX")
                #print(max_index)
                max_index_1 = playlist_score_df_only_score.max(axis = 0)
                playlist_max_from_the_loop.append(max_index_1[0])
                #print("MAX INDEX V")
                #print(max_index_1[0])
           # print(playlist_score_df_only_score)
           # print(max_index[0])

                best_cluster_df = track_features_DF_only_good_clusters[track_features_DF_only_good_clusters["clusters"] == max_index[0]]
                

               
                best_cluster_df_2 = track_features_DF[track_features_DF.index.isin(best_cluster_df.index)]
                best_cluster_df_2["iteration"] = i
           # print(best_cluster_df_2)
           # print(best_cluset_df_2)
                playlist_best_cluster_from_the_loop.append(max_index[0])
                datalist.append(best_cluster_df_2)
            

    elif(future_cond == 3):
        for i in range(50):
                print("CONDTION 3 MET")
                random_state_value = randrange(3000)    
           #     print(number_of_clusters)

                number_of_clusters_1 = randint(number_of_clusters-4,number_of_clusters+4)
                if(number_of_clusters_1 < 2):
                    number_of_clusters_1=2
                elif(track_features_DF.shape[0] / number_of_clusters_1 < 10):
                    number_of_clusters_1 = number_of_clusters

               # print("RANDOMCLUSTER = "+ str(number_of_clusters_1))
        #print(track_features_DF_filtered_for_clustering_scaled_cleaned)
                kmeans_obj = KMeans(n_clusters=number_of_clusters_1, init='k-means++', 
                max_iter=100, n_init=15, verbose=0, random_state=random_state_value)
       #print(kmeans_obj)
                kmeans_obj.fit(track_features_DF_filtered_for_clustering_scaled_cleaned)
        #print(kmeans_obj)
                kmeans_output = kmeans_obj.labels_

        
                cluster_sizes = Counter(kmeans_output)
       
                counter_np  = np.fromiter(cluster_sizes.values(), dtype=float)
                counter_np_key  = np.fromiter(cluster_sizes.keys(), dtype=int)

                big_clusters = counter_np_key[counter_np > 10]

                track_features_DF_filtered_for_clustering_scaled_cleaned["clusters"] = kmeans_output
        
                big_clusters_list = list(big_clusters)
                big_clusters_list_str = map(str, big_clusters_list)
        

                track_features_DF_only_good_clusters = track_features_DF_filtered_for_clustering_scaled_cleaned.query('clusters in @big_clusters_list_str')
                track_features_DF_only_good_clusters.columns = total_features_flat


       # print(track_features_DF_only_good_clusters)
       
   
                df_low_features = track_features_DF_only_good_clusters[list(final_selected_low_features)]
                low_means = (df_low_features.mean(axis = 1))
               # print("TRACK FEATURES FULL")
                #print(track_features_DF_only_good_clusters)
                #df_high_features = track_features_DF_only_good_clusters[final_selected_high_features]
               # print("final_selected_high_features")
               # print(final_selected_high_features)
               # print("DF_HIGH_FEATURES")
               # print(df_high_features)
                #high_means = (df_high_features.mean(axis = 1))
               # print("HIGH MEANS") 
                #print(high_means)
                track_features_DF_only_good_clusters["low_means"] = low_means
                #track_features_DF_only_good_clusters["high_means"] = high_means
                #print("TRACK FEATS HIGH MEANS MEANS") 
                #print(track_features_DF_only_good_clusters)

            #print(track_features_DF_only_good_clusters)
                playlist_score_df =  (track_features_DF_only_good_clusters
                    .assign(playlist_score = low_means)
                    .groupby("clusters")
                    .agg(['mean']))


                playlist_score_df_only_score = playlist_score_df["playlist_score"]
                max_index = playlist_score_df_only_score.idxmin(axis = 0)
                #print("MAX INDEX")
                #print(max_index)
                max_index_1 = playlist_score_df_only_score.min(axis = 0)
                playlist_max_from_the_loop.append(max_index_1[0])
                #print("MAX INDEX V")
                #print(max_index_1[0])
           # print(playlist_score_df_only_score)
           # print(max_index[0])

                best_cluster_df = track_features_DF_only_good_clusters[track_features_DF_only_good_clusters["clusters"] == max_index[0]]
                
                best_cluster_df_2 = track_features_DF[track_features_DF.index.isin(best_cluster_df.index)]
                best_cluster_df_2["iteration"] = i
           # print(best_cluster_df_2)
           # print(best_cluset_df_2)
                playlist_best_cluster_from_the_loop.append(max_index[0])
                datalist.append(best_cluster_df_2)
               # print(best_cluster_df_2)


            

    output_df = pd.DataFrame(playlist_max_from_the_loop, range(50), columns = ["score"])
    
    if (future_cond == 1 or future_cond == 2):
        output_df = output_df.sort_values(by=('score'), ascending=False)
    elif(future_cond == 2):
        output_df = output_df.sort_values(by=('score'), ascending=True)
        
        #print(output_df)
    output_df_unique = output_df.drop_duplicates(keep="first")
    if (output_df_unique.shape[0]) >= 3:
        output_df_top3 = output_df_unique.iloc[range(3), :]
    else:
        output_df_top3 = output_df.iloc[range(3), :]
        
    

    top3_clusters = list(output_df_top3.index.values)

   
    first_best_pst = datalist[top3_clusters[0]]
    second_best_pst = datalist[top3_clusters[1]]
    third_best_pst = datalist[top3_clusters[2]]

  #  print(third_best_pst.columns)

    first_best_tracks = first_best_pst["track_names"]
    second_best_tracks = second_best_pst["track_names"]
    third_best_tracks = third_best_pst["track_names"]

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

    
   # print("FIRST BEST TRACKS")
   # print(first_best_tracks)
   # print(list(first_best_tracks_uris))
   # print(type(first_best_tracks_uris))
    #print("INDEXED")
   # print(first_best_tracks_uris.iloc[3])

    ids_best_playlist_1 = [i.split('track:', 1)[1] for i in first_best_tracks_uris]
    #print(ids_best_playlist_1)

    

    best_playlist_1_track_info_list = []
    for n in range(len(first_best_tracks_uris)):
        playlist_api_endpoint = "{}/tracks/{}".format(SPOTIFY_API_URL, ids_best_playlist_1[n])
        playlists_response = requests.get(playlist_api_endpoint, headers=authorization_header)
        best_playlist_1_track_info = json.loads(playlists_response.text)
        best_playlist_1_track_info_list.append(best_playlist_1_track_info)

   # print("FULL")
   # print(best_playlist_1_track_info_list[0])
   # print("IMAGE SUBSET")
   # print(best_playlist_1_track_info_list[0]["album"]["images"])
   # print("IMAGE SUBSET")


    #print(best_playlist_1_track_info_list[0]["album"]["images"][0]["url"])


    best_playlist_1_artists = []
    for i in range(len(ids_best_playlist_1)):
        c_a = best_playlist_1_track_info_list[i]["album"]["artists"][0]["name"]
        best_playlist_1_artists.append(c_a)


    best_playlist_1_images = []
    for i in range(len(ids_best_playlist_1)):
        c_i = best_playlist_1_track_info_list[i]["album"]["images"][0]["url"]
        best_playlist_1_images.append(c_i)

   # print(best_playlist_1_images)
    #print("END")
    #print(first_best_tracks)

   # print("FULL LIST")
   # print(best_playlist_1_full_list)

    #access_token = access_token_dict["acc_t"]
    #sp = spotipy.Spotify(auth=access_token)

    ##first_best_tracks_info = []
    #for n in range(len(best_playlists_uris_list)):
     #   first_best_tracks_loop =  sp.tracks(first_best_tracks_uris.iloc[n])
      #  first_best_tracks_info.append(first_best_tracks_loop)



    ids_best_playlist_2 = [i.split('track:', 1)[1] for i in second_best_tracks_uris]
    #print(ids_best_playlist_1)


    best_playlist_2_track_info_list = []
    for n in range(len(second_best_tracks_uris)):
        playlist_api_endpoint = "{}/tracks/{}".format(SPOTIFY_API_URL, ids_best_playlist_2[n])
        playlists_response = requests.get(playlist_api_endpoint, headers=authorization_header)
        best_playlist_2_track_info = json.loads(playlists_response.text)
        best_playlist_2_track_info_list.append(best_playlist_2_track_info)

    
    best_playlist_2_artists = []
    for i in range(len(ids_best_playlist_2)):
        c_a = best_playlist_2_track_info_list[i]["album"]["artists"][0]["name"]
        best_playlist_2_artists.append(c_a)

    print(best_playlist_1_artists)

    best_playlist_2_images = []
    for i in range(len(ids_best_playlist_2)):
        c_i = best_playlist_2_track_info_list[i]["album"]["images"][0]["url"]
        best_playlist_2_images.append(c_i)

  #  access_token = access_token_dict["acc_t"]
   # sp = spotipy.Spotify(auth=access_token)






    ids_best_playlist_3 = [i.split('track:', 1)[1] for i in third_best_tracks_uris]


    best_playlist_3_track_info_list = []
    for n in range(len(third_best_tracks_uris)):
        playlist_api_endpoint = "{}/tracks/{}".format(SPOTIFY_API_URL, ids_best_playlist_3[n])
        playlists_response = requests.get(playlist_api_endpoint, headers=authorization_header)
        best_playlist_3_track_info = json.loads(playlists_response.text)
        best_playlist_3_track_info_list.append(best_playlist_3_track_info)

    
    best_playlist_3_artists = []
    for i in range(len(ids_best_playlist_3)):
        c_a = best_playlist_3_track_info_list[i]["album"]["artists"][0]["name"]
        best_playlist_3_artists.append(c_a)

    

    best_playlist_3_images = []
    for i in range(len(ids_best_playlist_3)):
        c_i = best_playlist_3_track_info_list[i]["album"]["images"][0]["url"]
        best_playlist_3_images.append(c_i)

  #  access_token = access_token_dict["acc_t"]
   # sp = spotipy.Spotify(auth=access_token)

    best_playlist_3_full_list = list(zip(best_playlist_3_images, third_best_tracks, best_playlist_3_artists, third_best_tracks_uris))

    best_playlist_2_full_list = list(zip(best_playlist_2_images, second_best_tracks, best_playlist_2_artists, second_best_tracks_uris))

    best_playlist_1_full_list = list(zip(best_playlist_1_images, first_best_tracks, best_playlist_1_artists, first_best_tracks_uris))


   # first_best_tracks_info = []
   # for n in range(len(best_playlists_uris_list)):
    #    first_best_tracks_loop =  sp.tracks(list(list(best_playlists_uris_list[1][0])))
     #   first_best_tracks_info.append(first_best_tracks_loop)

    #print(first_best_tracks_info)
    #print("ARTISTS")
    #print(first_best_tracks_info[0]["tracks"])





    playlist_1_non_scaled_df = track_features_DF.query('uri in @first_best_tracks_uris')
    

    if (final_selected_high_features[0] == 1):
        xxx = scaled_full_tracks_for_later[scaled_full_tracks_for_later.index.isin(first_best_pst.index)]
        
        xxx.columns = total_features_flat_1
        playlist_1_df_scaled = xxx 

        playlist_1_non_scaled_df_all_feats = playlist_1_df_scaled[final_selected_low_features]
        low_means = (playlist_1_non_scaled_df_all_feats.mean(axis = 1))
        playlist_1_non_scaled_df_all_feats["low_means"] = low_means
        playlist_1_non_scaled_df_score =  (playlist_1_non_scaled_df_all_feats
                    .filter(total_features_flat)
                    .assign(playlist_score = low_means)
                    .agg(['mean']))

    elif (final_selected_low_features[0] == 1):
       # print("CONDTIION 2")
        xxx = scaled_full_tracks_for_later[scaled_full_tracks_for_later.index.isin(first_best_pst.index)]
       # print(xxx)
        
        xxx.columns = total_features_flat_1
        playlist_1_df_scaled = xxx 

        playlist_1_non_scaled_df_all_feats = playlist_1_df_scaled[final_selected_high_features]
        high_means = (playlist_1_non_scaled_df_all_feats.mean(axis = 1))
        playlist_1_non_scaled_df_all_feats["high_means"] = high_means
        
        playlist_1_non_scaled_df_score =  (playlist_1_non_scaled_df_all_feats
                    .filter(total_features_flat)
                    .assign(playlist_score = high_means)
                    .agg(['mean']))

    else:
        #print("CONDTIION 3")

        #print(track_features_DF.columns)
        #print(first_best_pst)
        xxx = scaled_full_tracks_for_later[scaled_full_tracks_for_later.index.isin(first_best_pst.index)]
        #print(xxx)
        
        xxx.columns = total_features_flat_1
        playlist_1_df_scaled = xxx 

        
        #playlist_1_df_scaled = sk.preprocessing.scale(playlist_1_non_scaled_df_all_feats_0)
        #playlist_1_df_scaled = pd.DataFrame(playlist_1_df_scaled)

        #playlist_1_df_scaled.columns = total_features_flat_1

       # print(playlist_1_df_scaled)

        playlist_1_non_scaled_df_all_feats_1 = playlist_1_df_scaled[final_selected_high_features] 
       # print(playlist_1_non_scaled_df_all_feats_1)
        high_means = (playlist_1_non_scaled_df_all_feats_1.mean(axis = 1))

        playlist_1_non_scaled_df_all_feats_2 = playlist_1_df_scaled[final_selected_low_features]
       # print(playlist_1_non_scaled_df_all_feats_2)
        low_means = (playlist_1_non_scaled_df_all_feats_2.mean(axis = 1))
    
        playlist_1_df_scaled["high_means"] = high_means
        playlist_1_df_scaled["low_means"] = low_means

        playlist_1_non_scaled_df_score =  (playlist_1_df_scaled
                    .filter(total_features_flat)
                    .assign(playlist_score = high_means - low_means)
                    .agg(['mean']))


    if (final_selected_high_features[0] == 1):
       # print("COND1")
       # print("PLAYLIST SCORE")    
       # print(playlist_1_non_scaled_df_score)
       # print(playlist_1_non_scaled_df_score["playlist_score"][0])
        final_playlist_score = round(100*(100 - playlist_1_non_scaled_df_score["playlist_score"][0]))
       # print(final_playlist_score)

        first_playlist_score_string = "Playlist Score: " + str(final_playlist_score)
        #print(first_playlist_score_string)
    else:
        #print("COND2")
        #print("PLAYLIST SCORE")    
       # print(playlist_1_non_scaled_df_score)
       # print(playlist_1_non_scaled_df_score["playlist_score"][0])
        final_playlist_score = round(100*playlist_1_non_scaled_df_score["playlist_score"][0])
       # print(final_playlist_score)

        first_playlist_score_string = "Playlist Score: " + str(final_playlist_score)
       # print(first_playlist_score_string)



        #selected_high_features_inds = list(map(int, selected_high_features_inds))
    if (final_selected_high_features[0] == 1):
      #  print("CONDTIION 1")
        xxx = scaled_full_tracks_for_later[scaled_full_tracks_for_later.index.isin(second_best_pst.index)]
       # print(xxx)
        
        xxx.columns = total_features_flat_1
        playlist_1_df_scaled = xxx 

        playlist_1_non_scaled_df_all_feats = playlist_1_df_scaled[final_selected_low_features]
        low_means = (playlist_1_non_scaled_df_all_feats.mean(axis = 1))
        playlist_1_non_scaled_df_all_feats["low_means"] = low_means
        playlist_1_non_scaled_df_score =  (playlist_1_non_scaled_df_all_feats
                    .filter(total_features_flat)
                    .assign(playlist_score = low_means)
                    .agg(['mean']))

    elif (final_selected_low_features[0] == 1):
       # print("CONDTIION 2")
        xxx = scaled_full_tracks_for_later[scaled_full_tracks_for_later.index.isin(second_best_pst.index)]
       # print(xxx)
        
        xxx.columns = total_features_flat_1
        playlist_1_df_scaled = xxx 

        playlist_1_non_scaled_df_all_feats = playlist_1_df_scaled[final_selected_high_features]
        high_means = (playlist_1_non_scaled_df_all_feats.mean(axis = 1))
        playlist_1_non_scaled_df_all_feats["high_means"] = high_means
        
        playlist_1_non_scaled_df_score =  (playlist_1_non_scaled_df_all_feats
                    .filter(total_features_flat)
                    .assign(playlist_score = high_means)
                    .agg(['mean']))

    else:
       # print("CONDTIION 3")

       # print(track_features_DF.columns)
       # print(first_best_pst)
        xxx = scaled_full_tracks_for_later[scaled_full_tracks_for_later.index.isin(second_best_pst.index)]
       # print(xxx)
        
        xxx.columns = total_features_flat_1
        playlist_1_df_scaled = xxx 

        
        #playlist_1_df_scaled = sk.preprocessing.scale(playlist_1_non_scaled_df_all_feats_0)
        #playlist_1_df_scaled = pd.DataFrame(playlist_1_df_scaled)

        #playlist_1_df_scaled.columns = total_features_flat_1

       # print(playlist_1_df_scaled)

        playlist_1_non_scaled_df_all_feats_1 = playlist_1_df_scaled[final_selected_high_features] 
       # print(playlist_1_non_scaled_df_all_feats_1)
        high_means = (playlist_1_non_scaled_df_all_feats_1.mean(axis = 1))

        playlist_1_non_scaled_df_all_feats_2 = playlist_1_df_scaled[final_selected_low_features]
       # print(playlist_1_non_scaled_df_all_feats_2)
        low_means = (playlist_1_non_scaled_df_all_feats_2.mean(axis = 1))
    
        playlist_1_df_scaled["high_means"] = high_means
        playlist_1_df_scaled["low_means"] = low_means

        playlist_1_non_scaled_df_score =  (playlist_1_df_scaled
                    .filter(total_features_flat)
                    .assign(playlist_score = high_means - low_means)
                    .agg(['mean']))


    if (final_selected_high_features[0] == 1):
      # # print("COND1")
      #  print("PLAYLIST SCORE")    
      #  print(playlist_1_non_scaled_df_score)
      #  print(playlist_1_non_scaled_df_score["playlist_score"][0])
        final_playlist_score = round(100*(100 - playlist_1_non_scaled_df_score["playlist_score"][0]))
      #  print(final_playlist_score)

        second_playlist_score_string = "Playlist Score: " + str(final_playlist_score)
      #  print(second_playlist_score_string)
    else:
       # print("COND2")
       # print("PLAYLIST SCORE")    
       # print(playlist_1_non_scaled_df_score)
       # print(playlist_1_non_scaled_df_score["playlist_score"][0])
        final_playlist_score = round(100*playlist_1_non_scaled_df_score["playlist_score"][0])
      #  print(final_playlist_score)

        second_playlist_score_string = "Playlist Score: " + str(final_playlist_score)
      #  print(second_playlist_score_string)







        #selected_high_features_inds = list(map(int, selected_high_features_inds))
    if (final_selected_high_features[0] == 1):
      #  print("CONDTIION 1")
        xxx = scaled_full_tracks_for_later[scaled_full_tracks_for_later.index.isin(third_best_pst.index)]
      #  print(xxx)
        
        xxx.columns = total_features_flat_1
        playlist_1_df_scaled = xxx 

        playlist_1_non_scaled_df_all_feats = playlist_1_df_scaled[final_selected_low_features]
        low_means = (playlist_1_non_scaled_df_all_feats.mean(axis = 1))
        playlist_1_non_scaled_df_all_feats["low_means"] = low_means
        playlist_1_non_scaled_df_score =  (playlist_1_non_scaled_df_all_feats
                    .filter(total_features_flat)
                    .assign(playlist_score = low_means)
                    .agg(['mean']))

    elif (final_selected_low_features[0] == 1):
       # print("CONDTIION 2")
        xxx = scaled_full_tracks_for_later[scaled_full_tracks_for_later.index.isin(third_best_pst.index)]
        
        xxx.columns = total_features_flat_1
        playlist_1_df_scaled = xxx 

        playlist_1_non_scaled_df_all_feats = playlist_1_df_scaled[final_selected_high_features]
        high_means = (playlist_1_non_scaled_df_all_feats.mean(axis = 1))
        playlist_1_non_scaled_df_all_feats["high_means"] = high_means
        
        playlist_1_non_scaled_df_score =  (playlist_1_non_scaled_df_all_feats
                    .filter(total_features_flat)
                    .assign(playlist_score = high_means)
                    .agg(['mean']))

    else:
       # print("CONDTIION 3")

       # print(track_features_DF.columns)
       # print(first_best_pst)
        xxx = scaled_full_tracks_for_later[scaled_full_tracks_for_later.index.isin(third_best_pst.index)]
       # print(xxx)
        
        xxx.columns = total_features_flat_1
        playlist_1_df_scaled = xxx 

        
        #playlist_1_df_scaled = sk.preprocessing.scale(playlist_1_non_scaled_df_all_feats_0)
        #playlist_1_df_scaled = pd.DataFrame(playlist_1_df_scaled)

        #playlist_1_df_scaled.columns = total_features_flat_1

       # print(playlist_1_df_scaled)

        playlist_1_non_scaled_df_all_feats_1 = playlist_1_df_scaled[final_selected_high_features] 
       # print(playlist_1_non_scaled_df_all_feats_1)
        high_means = (playlist_1_non_scaled_df_all_feats_1.mean(axis = 1))

        playlist_1_non_scaled_df_all_feats_2 = playlist_1_df_scaled[final_selected_low_features]
      #  print(playlist_1_non_scaled_df_all_feats_2)
        low_means = (playlist_1_non_scaled_df_all_feats_2.mean(axis = 1))
    
        playlist_1_df_scaled["high_means"] = high_means
        playlist_1_df_scaled["low_means"] = low_means

        playlist_1_non_scaled_df_score =  (playlist_1_df_scaled
                    .filter(total_features_flat)
                    .assign(playlist_score = high_means - low_means)
                    .agg(['mean']))


    if (final_selected_high_features[0] == 1):
       # print("COND1")
       # print("PLAYLIST SCORE")    
       # print(playlist_1_non_scaled_df_score)
       # print(playlist_1_non_scaled_df_score["playlist_score"][0])
        final_playlist_score = round(100*(100 - playlist_1_non_scaled_df_score["playlist_score"][0]))
       # print(final_playlist_score)

        third_playlist_score_string = "Playlist Score: " + str(final_playlist_score)
       # print(third_playlist_score_string)
    else:
      #  print("COND2")
       # print("PLAYLIST SCORE")    
       # print(playlist_1_non_scaled_df_score)
       # print(playlist_1_non_scaled_df_score["playlist_score"][0])
        final_playlist_score = round(100 * playlist_1_non_scaled_df_score["playlist_score"][0])
        #print(final_playlist_score)

        third_playlist_score_string = "Playlist Score: " + str(final_playlist_score)
      #  print(third_playlist_score_string)

    




    best_playlists_full_list = list()
    best_playlists_full_list.append(best_playlist_1_full_list)
    best_playlists_full_list.append(best_playlist_2_full_list)
    best_playlists_full_list.append(best_playlist_3_full_list)
        
    session["best_p_list"] = best_playlists_full_list

    return render_template("playlist_showcase.html", first_best_tracks = best_playlist_1_full_list, 
        second_best_tracks = best_playlist_2_full_list, third_best_tracks = best_playlist_3_full_list, 
        first_playlist_score_string = first_playlist_score_string, second_playlist_score_string = second_playlist_score_string,
        third_playlist_score_string = third_playlist_score_string)



@app.route("/callback/playlist_upload_page", methods=["GET", "POST"])
def playlist_upload():
    if request.method == 'POST':
        if request.form.get('upload_playlist_1_button') == "Upload Playlist":
            playlist_selected_for_upload = 1 
        elif request.form.get('upload_playlist_2_button') == "Upload Playlist":
            playlist_selected_for_upload = 0
        elif request.form.get('upload_playlist_3_button') == "Upload Playlist":
            playlist_selected_for_upload = 2

   # print(playlist_selected_for_upload)

    session["playlist_index"] = playlist_selected_for_upload

    
    #print(best_playlist_full_list)

    best_playlists_full_list = session.get("best_p_list")
    best_playlist_1_full_list = best_playlists_full_list[0]
    best_playlist_2_full_list = best_playlists_full_list[1]
    best_playlist_3_full_list = best_playlists_full_list[2]

    return render_template("name_new_playlist.html", first_best_tracks = best_playlist_1_full_list, 
        second_best_tracks = best_playlist_2_full_list, third_best_tracks = best_playlist_3_full_list)

@app.route("/callback/playlist_create_page", methods=["GET", "POST"])
def playlist_create():
    authorization_header = session.get("a_h")
    access_token = session.get("a_t")
    new_playlist_name = request.form["Name Your New Playlist"]
    playlist_selected_for_upload = session.get("playlist_index")

  #  print(new_playlist_name)
  #  print(authorization_header)
   

    best_playlists_full_list = session.get("best_p_list")
    best_playlist_1_full_list = best_playlists_full_list[0]
    best_playlist_2_full_list = best_playlists_full_list[1]
    best_playlist_3_full_list = best_playlists_full_list[2]

 


    

    p1_uris = [i[3] for i in best_playlist_1_full_list]
    p2_uris = [i[3] for i in best_playlist_2_full_list]
    p3_uris = [i[3] for i in best_playlist_3_full_list]

  





   # p1_uris = best_playlist_1_full_list[3]
    #p2_uris = best_playlist_2_full_list[3]
    #p3_uris = best_playlist_3_full_list[3]

    best_playlists_uris_FINAL = list()
    best_playlists_uris_FINAL.append(p1_uris)
    best_playlists_uris_FINAL.append(p2_uris)
    best_playlists_uris_FINAL.append(p3_uris)
    
    #print(access_token1)

    sp = spotipy.Spotify(auth=access_token)

    user_all_data = sp.current_user()
    USER_ID = user_all_data["id"]

    playlist_all_data = sp.user_playlist_create(USER_ID, str(new_playlist_name))
    new_playlist_id = playlist_all_data["id"]

 


   

    selected_playlist_song_uris = best_playlists_uris_FINAL[playlist_selected_for_upload]

    sp.user_playlist_add_tracks(USER_ID, new_playlist_id, selected_playlist_song_uris)

    return render_template("final_page.html", first_best_tracks = best_playlist_1_full_list, 
        second_best_tracks = best_playlist_2_full_list, third_best_tracks = best_playlist_3_full_list)




if __name__ == "__main__":
    app.run(debug=True, port=PORT)
    