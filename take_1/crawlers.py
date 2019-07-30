# coding=utf-8
import time
import datetime
from pytrends.request import TrendReq
import spotipy
import pandas as pd
import requests
from bs4 import BeautifulSoup
from spotipy.oauth2 import SpotifyClientCredentials
import logging

########################### fill before running ##############

client_credentials_manager = SpotifyClientCredentials(client_id='a021abf7a1f14cf4a62678e593dde4b6',
                                                      client_secret='d5a27f392df14cbfbb702aed156547a8')
START_INDEX = 647
END_INDEX = 774

########################### constants and globals ###########################

sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

pytrends = TrendReq(hl='en-US', tz=360)

logging.basicConfig(filename=r'crawlers_log_{start}_{end}.log'.format(start=START_INDEX, end=END_INDEX),
                    level=logging.INFO)
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

errors_count = 0


############################### functions #####################


# from spotify
def get_artist_popularity(name):
    logging.info('get_artist_popularity (spotify API) ' + str(datetime.datetime.now()))
    time.sleep(2)
    results = sp.search(q='artist:' + name, type='artist')
    if len(results['artists']['items']) > 0:
        artist = results['artists']['items'][0]
        return artist['popularity']
    return None

# from google trends - youtube searches
def get_countries_rank(song_name):
    logging.info('get_countries_rank (pytrends) ' + str(datetime.datetime.now()))
    time.sleep(4)
    try:
        song_name = str(song_name)
    except:
        logging.error("can't convert song to str: " + song_name + " " + str(datetime.datetime.now()))

    pytrends.build_payload([song_name], cat=0, timeframe="2018-01-01 2018-11-01", gprop="youtube")
    countries_df = pytrends.interest_by_region(resolution="COUNTRY").reset_index()
    countries = countries_df['geoName'].tolist()
    ranks = countries_df[song_name].tolist()

    return dict(zip(countries, ranks))


def fix_url(url):  # correct relative urls back to absolute urls
    if url[0] == '/':
        return 'https://www.youtube.com' + url
    else:
        return url

# gets views and days since upload from youtube.
def get_stats(track_and_artist):
    logging.info('get_stats (youtube crawling) ' + str(datetime.datetime.now()))
    time.sleep(2)
    search_url = "https://www.youtube.com/results?search_query=" + track_and_artist.replace(" ", "+")
    soup = BeautifulSoup(requests.get(search_url).text, 'html.parser')
    items = soup('a', class_="yt-uix-tile-link")
    if items:
        song_url = fix_url(items[0]['href'])
    else:
        return None, None
    soup = BeautifulSoup(requests.get(song_url).text, 'html.parser')
    views = soup.find('div', class_='watch-view-count')
    if views:
        views = views.text.replace(" views", "").replace(",", "")
    date = soup.find('strong', class_="watch-time-text")
    if date:
        date = date.text[len('Published on '):]
    return views, date


###############################################################

def process_one_file(file_index):
    global errors_count
    if errors_count > 5:
        return
    logging.info("running crawlers on file number " + file_index)
    mini_spotify_songs = pd.read_csv(r'splitSpotifyFeatures\mini_basic_songs_100_{index}.csv'.format(index=file_index),
                                     encoding="utf-8")
    mini_spotify_songs['simple_track_name'] = mini_spotify_songs.track_name.apply(
        lambda x: x.replace('(', ',').replace('-', ',').replace('feat.', ',').split(',')[0])
    mini_spotify_songs[
        'simple_track_and_artist'] = mini_spotify_songs.simple_track_name + " " + mini_spotify_songs.artist_name
    mini_spotify_songs["artist_popularity"] = mini_spotify_songs["artist_name"].apply(get_artist_popularity)

    countries_by_track = mini_spotify_songs.simple_track_name.apply(lambda x: pd.Series(get_countries_rank(x)))
    mini_spotify_songs = mini_spotify_songs.merge(countries_by_track, how='outer', left_index=True,
                                                  right_index=True)
    mini_spotify_songs["date_and_views"] = mini_spotify_songs.simple_track_and_artist.apply(get_stats)

    mini_spotify_songs.to_csv(r'processed_split_features\mini_processed_songs_100_{index}.csv'.format(index=file_index),
                              encoding="utf-8")
    logging.info("done crwaling on file number " + file_index)


def run_data_crawlers(start_index, end_index):
    for i in range(end_index + 1 - start_index):
        process_one_file(str(start_index + i))


run_data_crawlers(START_INDEX, END_INDEX)

