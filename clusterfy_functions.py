
import numpy as np
from random import randint
from random import randrange
from sklearn.cluster import KMeans
import sklearn as sk
from collections import Counter, defaultdict
import pandas as pd
import spotipy
import spotipy.util as util

##function to get the track artist and album image using track ids
def get_track_info(track_ids, access_token):
            #get the access token 
        sp = spotipy.Spotify(auth=access_token)

        def chunks(l, n):
            for i in range(0, len(l), n):
                yield l[i:i + n]

        ##get track info in chunks, as spotify limits the maximum number of tracks you can request at once
        ids_chunked = list(chunks(track_ids, 2))
        track_artists = []
        track_images = []

        if len(ids_chunked[-1]) % 2 != 0:
            del ids_chunked[-1]

        print("LENGTH CUNKED")
        print(len(ids_chunked))    

        for i in range(len(ids_chunked)):

            track_info_list_full = sp.tracks(ids_chunked[i])

            for i in range(len(track_info_list_full["tracks"])):
                c_a = track_info_list_full["tracks"][i]["artists"][0]["name"]
                track_artists.append(c_a)

            for i in range(len(track_info_list_full["tracks"])):
                c_a = track_info_list_full["tracks"][i]["album"]["images"][0]["url"]
                track_images.append(c_a)

        return track_artists, track_images

        


def clusterfy_function(track_features_DF, track_features_DF_for_clustering, selected_low_features, selected_high_features, condition):

        #create the total features vector
        total_features_flat = np.zeros(0)
        if(condition == "both"):
            total_features_flat = np.concatenate((selected_low_features, selected_high_features), axis=None)
        elif(condition == "max"):
            total_features_flat = selected_high_features.copy()
        elif(condition == "min"):
            total_features_flat = selected_low_features.copy()

        total_features_flat = np.append(total_features_flat, "clusters")
        playlist_best_cluster_from_the_loop = []
        playlist_max_from_the_loop = []
        datalist = list()

        
        ##Set a default number of clusters for the K-means with 6 clusters minimum
        number_of_clusters = track_features_DF.shape[0] / 10
        number_of_clusters = round(number_of_clusters)

        if (number_of_clusters > 6):
            number_of_clusters = 6
        
        
        ##do 50 runs of the K-means clustering algorithm
        for i in range(50):
             
            ##determine the number of clusters, I set this value to be slightly different in each run
            number_of_clusters_1 = randint(number_of_clusters - 4,number_of_clusters + 4)
            if(number_of_clusters_1 < 2):
                number_of_clusters_1 = 2
            elif(track_features_DF.shape[0] / number_of_clusters_1 < 10):
                number_of_clusters_1 = number_of_clusters

            ##generate a value for the random state
            #run K-means
            kmeans_obj = KMeans(n_clusters=number_of_clusters_1, init='k-means++', 
            max_iter=100, n_init=15, verbose=0)
            kmeans_obj.fit(track_features_DF_for_clustering)
       
            #extract the labels
            kmeans_output = kmeans_obj.labels_
            track_features_DF_for_clustering["clusters"] = kmeans_output

            #extract the cluster sizes
            cluster_sizes = Counter(kmeans_output)
            counter_np  = np.fromiter(cluster_sizes.values(), dtype=float)
            counter_np_key  = np.fromiter(cluster_sizes.keys(), dtype=int)

            #keep only the clusters with over 10 songs
            big_clusters = counter_np_key[counter_np > 10]
            big_clusters_list = list(big_clusters)
            big_clusters_list_str = map(str, big_clusters_list)
            track_features_DF_only_good_clusters = track_features_DF_for_clustering.query(
                'clusters in @big_clusters_list_str')
            track_features_DF_only_good_clusters.columns = total_features_flat

            ##if both max and min features were picked
            if condition == "both":
                    df_low_features = track_features_DF_only_good_clusters[list(selected_low_features)]
                    low_means = (df_low_features.mean(axis = 1))

                    df_high_features = track_features_DF_only_good_clusters[list(selected_high_features)]
                    high_means = (df_high_features.mean(axis = 1))
                    
                    track_features_DF_only_good_clusters["low_means"] = low_means
                    track_features_DF_only_good_clusters["high_means"] = high_means
                    playlist_score_df =  (track_features_DF_only_good_clusters
                        .assign(playlist_score = high_means - low_means)
                        .groupby("clusters")
                        .agg(['mean']))

                    playlist_score_df_only_score = playlist_score_df["playlist_score"]
                    max_index = playlist_score_df_only_score.idxmax(axis = 0)
                    max_index_1 = playlist_score_df_only_score.max(axis = 0)
                    playlist_max_from_the_loop.append(max_index_1[0])

            #if only max features were picked
            if condition == "max":
                    df_high_features = track_features_DF_only_good_clusters[selected_high_features]
                    high_means = (df_high_features.mean(axis = 1))

                    track_features_DF_only_good_clusters["high_means"] = high_means
                    playlist_score_df =  (track_features_DF_only_good_clusters
                        .assign(playlist_score = high_means)
                        .groupby("clusters")
                        .agg(['mean']))

                    playlist_score_df_only_score = playlist_score_df["playlist_score"]
                    max_index = playlist_score_df_only_score.idxmax(axis = 0)
                    max_index_1 = playlist_score_df_only_score.max(axis = 0)
                    playlist_max_from_the_loop.append(max_index_1[0])

            #if only min features were picked
            if condition == "min":
                    df_low_features = track_features_DF_only_good_clusters[list(selected_low_features)]
                    low_means = (df_low_features.mean(axis = 1))

                    track_features_DF_only_good_clusters["low_means"] = low_means
                    playlist_score_df = (track_features_DF_only_good_clusters
                        .assign(playlist_score = low_means * -1)
                        .groupby("clusters")
                        .agg(['mean']))

                    playlist_score_df_only_score = playlist_score_df["playlist_score"]
                    max_index = playlist_score_df_only_score.idxmax(axis = 0)
                    max_index_1 = playlist_score_df_only_score.max(axis = 0)
                    playlist_max_from_the_loop.append(max_index_1[0])


            best_cluster_df = track_features_DF_only_good_clusters[track_features_DF_only_good_clusters["clusters"] == max_index[0]]
            best_cluster_df_2 = track_features_DF[track_features_DF.index.isin(best_cluster_df.index)]
            best_cluster_df_2["iteration"] = i
            #with each run append the playlist with the most fitting playlist score
            playlist_best_cluster_from_the_loop.append(max_index[0])
            datalist.append(best_cluster_df_2)

        output_df = pd.DataFrame(playlist_max_from_the_loop, range(50), columns = ["score"])

        if (condition == "both" or condition == "max" or condition == "min"):
            output_df = output_df.sort_values(by=('score'), ascending=False)
            
        #keep only the clusters/playllists with unique scores, so that the 3 showcased playlists
        #are unique     
        output_df_unique = output_df.drop_duplicates(keep="first")
        if (output_df_unique.shape[0]) >= 3:
            output_df_top3 = output_df_unique.iloc[range(3), :]
        else:
            output_df_top3 = output_df.iloc[range(3), :]
            
        top3_clusters = list(output_df_top3.index.values)

        #save the top 3 clusters/playlists into seperate lists
        first_best_pst = datalist[top3_clusters[0]]
        second_best_pst = datalist[top3_clusters[1]]
        third_best_pst = datalist[top3_clusters[2]]


        return first_best_pst, second_best_pst, third_best_pst








