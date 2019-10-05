

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

    
