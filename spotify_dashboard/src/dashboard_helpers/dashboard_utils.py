import os
import sys
import json
import numpy as np
import pandas as pd

def fill_missing_features(data: pd.DataFrame) -> pd.DataFrame:
    """
    Fill missing feature values in the dataframe using duplicate songs by the same artist
    that have complete feature sets.

    Parameters:
    data (pd.DataFrame): DataFrame containing song features and metadata.

    Returns:
    pd.DataFrame: DataFrame with missing feature values filled where possible.
    """
    # Check if at least one of the feature values is missing
    feature_names = [
        'acousticness', 'danceability', 'energy','instrumentalness', 'key'
        , 'liveness', 'loudness', 'mode','speechiness', 'tempo', 'valence'
    ]
    missing_features_mask = (data.loc[:,feature_names].isnull().sum(axis=1) > 0).values

    # Get track and artist names for songs with missing features & also find duplicates based on song + artist name
    missing_features_track_names = data.loc[missing_features_mask, 'track_name'].values
    missing_features_first_artist_names = data.loc[missing_features_mask, 'first_artist_name'].values
    duplicate_song_artist_combinations = data.duplicated(subset=['track_name','first_artist_name'],keep=False).values

    # Use above masks to find songs with missing features that also have duplicates with complete features (via ~missing_features_mask).
    # These duplicates with complete feature sets can be used to fill in the missing values of the songs with missing features.
    songs_with_fillable_features = data.loc[
        (data['track_name'].isin(missing_features_track_names) & data['first_artist_name'].isin(missing_features_first_artist_names))
        & ~missing_features_mask, 'track_name'
    ].values

    # Next, make sure that we exclude cases from the songs with fillable features where the song names are equivalent but 
    # the artist name is different.
    final_filter = data['track_name'].isin(songs_with_fillable_features) & duplicate_song_artist_combinations

    # Using the final_filter, separate out the dataframe into two parts: remainder_df (songs that cannot/don't need to be filled) 
    # and filled_df (songs that can be filled - e.g. The End of Heartache by Killswitch Engage).
    remainder_df = data.loc[~final_filter, :]
    filled_df = data.loc[final_filter,:].sort_values(
        by=['first_artist_name','track_name','valence'] # sorting by one of the features (here 'valence') ensures that the row that contains values is on top of the row that contains the missing values
    ).reset_index(drop=True) 
    filled_df.loc[:,'acousticness':'valence'] = filled_df.loc[:,'acousticness':'valence'].ffill() 

    # Lastly, combine the two dataframes back together and sort by index to restore original order.
    data = pd.concat([remainder_df, filled_df], axis=0).sort_index()

    return data
    

def assign_main_genre(data: pd.DataFrame) -> pd.DataFrame:
    """
    Assign a main genre to each artist based on the genres associated with their songs.
    For artists with multiple genre tags, the most frequently occurring genre is selected.
    In case of ties, the genre with the highest average rank (i.e., lowest average numerical rank) is chosen.

    Parameters:
    data (pd.DataFrame): DataFrame containing 'first_artist_name' and 'artist_genres' columns.

    Returns:
    pd.DataFrame: DataFrame with an additional 'main_genre' column assigned to each artist.
    """
    # Aggregate by first_artist_name and the corresponding artist_genres. This is done to find artists that have differing 
    # genre tags across songs. These artists will need special handling to assign a main genre. 
    agg_df = data.groupby(['first_artist_name', 'artist_genres'],dropna=False).agg({
        'id': 'count'
    }).reset_index()
    agg_df['artist_genres'] = agg_df['artist_genres'].fillna('Unknown')
    agg_df['duplicate_artist'] = agg_df.duplicated(subset=['first_artist_name'], keep=False)
    dup_df = agg_df.loc[agg_df['duplicate_artist']].reset_index(drop=True) # stores artists with varying genre tags
    non_dup_df = agg_df.loc[~agg_df['duplicate_artist']].reset_index(drop=True) # stores artists with indentical genre tags

    # Prepare non-duplicate dataframe by simply taking the first genre listed as the main genre
    non_dup_df['main_genre'] = [i.split(', ')[0] if pd.notna(i) else 'Unknown' for i in non_dup_df['artist_genres'].values]
    non_dup_df = non_dup_df.loc[:, ['first_artist_name', 'main_genre']]

    # Prepare duplicate dataframe by finding the most frequently occuring genre across all songs by the artist.
    # In case of ties, the genre with the highest average rank (i.e. lowest average numerical rank) is selected.
    # This way, we make sure that the genre with the most frequent appearance at the top of the genre list is selected.
    main_genre_list = []

    for artist in dup_df['first_artist_name'].unique():
        # Create a list of all genres that are associated with the artist by splitting the genre strings
        # Also preserve the positional information of the genres by assigning ranks based on their position 
        # in the genre string.
        genre_list = []
        rank_list = []
        for i in dup_df.loc[dup_df['first_artist_name']==artist,'artist_genres'].values:
            splitted_genres = i.split(', ')
            ranks = list(np.arange(1,len(splitted_genres)+1,1))
            genre_list.extend(splitted_genres)
            rank_list.extend(ranks)

        # Create a dataframe to count occurrences of each genre and calculate average rank
        main_genre_df = pd.DataFrame({
            'first_artist_name': artist, 
            'genres': genre_list, 
            'ranks': rank_list, 
            'helper_col': 1  # only needed to have a column to count occurrences
        })
        main_genre_df = main_genre_df.groupby(['first_artist_name','genres']).agg({
            'helper_col': 'sum'
            , 'ranks': 'mean'
        }).reset_index().rename(
            columns={
                'helper_col': 'genre_occurence',
                'genres': 'main_genre'
        }).sort_values(
            by=['genre_occurence','ranks'], ascending=[False, True]
        ).reset_index(drop=True)

        # Special case for Eurotrance: If hard house, trance and eurodance are all present, classify as eurotrance (which is not a Spotify genre)
        if len(np.intersect1d(['hard house', 'trance', 'eurodance'], main_genre_df['main_genre'])) == 3:
            check_df = pd.DataFrame({'first_artist_name': [artist], 'main_genre': ['eurotrance']})
        else:
            check_df = pd.DataFrame(main_genre_df.loc[0, ['first_artist_name','main_genre']]).transpose()
        main_genre_list.append(check_df)

    # Combine cleaned duplicate and non-duplicate dataframes
    dup_df_cleaned = pd.concat(main_genre_list, axis=0).reset_index(drop=True)
    main_genre_df = pd.concat([dup_df_cleaned, non_dup_df], axis=0).reset_index(drop=True)

    # Finally merge the main_genres back to the original dataframe
    data = data.merge(main_genre_df, how='left', on='first_artist_name')
    
    return data


def assign_simplified_main_genre(data: pd.DataFrame) -> pd.DataFrame:
    """
    Simplify the main genres by selecting the most frequently occurring words across all main genres.
    This way, words that relate to subgenres are dropped, and words present across various subgenres are kept.

    Parameters:
    data (pd.DataFrame): DataFrame containing a 'main_genre' column.

    Returns:
    pd.DataFrame: DataFrame with an additional 'simplified_main_genre' column.
    """
    # Simplify main genres by selecting the most frequently occuring words across all main genres. 
    # This way, words that rather relate to the subgenre (e.g. 'hard' in 'hard house') are dropped 
    # and the words that are present across various subgenres are kept (here: 'house')
    subgenre_counts = data['main_genre'].value_counts().reset_index()

    sub_df_list = []
    for idx, row in subgenre_counts.iterrows():
        splitted_main_genres = row['main_genre'].split(' ')
        sub_df = pd.DataFrame({
            'main_genre':row['main_genre'], 
            'simplified_main_genre':splitted_main_genres, 
            'count': row['count'], 
            'index': idx
        })
        sub_df_list.append(sub_df)

    simplified_genre_df = pd.concat(sub_df_list,axis=0)
    total_occruences_df = simplified_genre_df.groupby('simplified_main_genre').agg({
        'count':'sum'
    }).reset_index().rename(columns={'count': 'total_count'}).sort_values(
        by='total_count', ascending=False
    ).reset_index(drop=True)

    simplified_genre_df = simplified_genre_df.merge(total_occruences_df, how='left', on='simplified_main_genre')
    simplified_genre_df = simplified_genre_df.sort_values(by=['index','total_count'], ascending=[True, False]).drop_duplicates(
        subset=['index'],keep='first'
    ).reset_index(drop=True)
    simplified_genre_df = simplified_genre_df.loc[:, ['main_genre', 'simplified_main_genre']]

    # Finally merge the simplified main genres back to the original dataframe
    data = data.merge(simplified_genre_df, how='left', on='main_genre')

    return data


def convert_track_duration(data: pd.DataFrame) -> pd.DataFrame:
    """
    Convert track duration from milliseconds to seconds and mm:ss format.

    Parameters:
    data (pd.DataFrame): DataFrame containing 'track_duration_ms' column.

    Returns:
    pd.DataFrame: DataFrame with additional 'track_duration_sec' and 'track_duration_min_sec' columns.
    """
    # Convert track_duration_ms to seconds
    data['track_duration_sec'] = data['track_duration_ms'].apply(float) / 1000

    # Convert track_duration_ms to mm:ss format
    data['track_duration_min_sec'] = pd.to_datetime(data['track_duration_ms'], unit='ms').dt.strftime('%M:%S')

    return data


def add_fully_played_label(data: pd.DataFrame, fully_played_threshold: float = 0.95) -> pd.DataFrame:
    """
    Add a label indicating whether the track was fully played based on the time delta to the next song.

    Parameters:
    data (pd.DataFrame): DataFrame containing 'played_at' and 'track_duration_sec' columns.
    fully_played_threshold (float): Threshold to consider a track as fully played (default is 0.95).

    Returns:
    pd.DataFrame: DataFrame with an additional 'track_fully_played' column.
    """
    # Determine the time delta to the next song played (in seconds)
    data = data.sort_values(by='played_at', ascending=True).reset_index()
    data['delta_to_next_song'] = pd.to_datetime(data['played_at']).diff().dt.seconds
    data['delta_to_next_song'] = data['delta_to_next_song'].shift(periods=-1)
    data['delta_to_next_song'] = data['delta_to_next_song'].fillna(data['track_duration_sec'])
    data = data.sort_values(by='index').reset_index(drop=True).drop(labels='index',axis=1)

    # Now determine the time played for each track. Since there is no direct information on time played provided 
    # by Spotify, we approximate it by taking the minimum of the track duration and the time delta to the next song. 
    # This way, we assume that the track was played until the next song started, but at maximum until the end of the track duration.
    data['track_time_played'] = np.min([data['track_duration_sec'].values, data['delta_to_next_song'].values],axis=0)

    # Determine whether track was fully played
    data['track_fully_played'] = data.apply(
        lambda x: 1 if x['track_duration_sec'] * fully_played_threshold <= x['delta_to_next_song'] else 0
        , axis=1
        )

    return data
