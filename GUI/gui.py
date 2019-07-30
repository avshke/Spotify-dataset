from tkinter import *
import pandas as pd
import webbrowser
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import tkinter.messagebox
from math import pi
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy

# files: random_songs- around 50,000 songs
random_songs = 'random_songs_processed_dataset.csv'
# countries_songs- around 75,000 most popular songs in 53 countries
countries_songs = 'weighted_means.csv'

COUNTRIES=['Argentina','Australia','Austria','Belgium','Bolivia','Brazil','Canada','Chile',
           'Colombia','Costa Rica','Czech Republic','Denmark','Dominican Republic', 'Ecuador',
           'El Salvador','Estonia','Finland','France','Germany','Greece','Guatemala','Honduras',
            'Hong Kong','Hungary','Iceland','Indonesia','Ireland','Italy','Japan','Latvia',
            'Lithuania','Malaysia','Mexico','Netherlands','New Zealand','Norway','Panama',
            'Paraguay','Peru','Philippines','Poland','Portugal','Singapore','Slovakia','Spain',
            'Sweden','Switzerland','Taiwan','Turkey','United Kingdom','United States',
            'Uruguay', 'Global']

original_countries = {
            'Bolivia':'Bolivia: Plurinational State of','Taiwan':'Taiwan: Province of China',
            'United Kingdom':'United Kingdom of Great Britain and Northern Ireland',
            'United States':'United States of America'}

dictcountries = { i : 0 for i in COUNTRIES }

class Gui:
    def __init__(self, checkbox_dict):
        self.root = Tk()
        self.root.title("SONG'S FEATURES")
        self.root.geometry('1300x1000')
        self.leftFrame = Frame(self.root)
        self.leftFrame.grid(sticky = W+N, row = 0, column = 0)
        self.rightFrame = Frame(self.root)
        self.rightFrame.grid(sticky = E, row = 0, column = 40)
        # initialize labels and entries
        self.name_song = Label(self.leftFrame, text = 'Song', height = 4 )
        self.name_song.grid(row = 28, column = 1, sticky = N+E)
        self.name_song.config(font= ('castellar', 12))
        self.artist_name = Label(self.leftFrame, text ='Artist', height =4)
        self.artist_name.grid(row = 30, column = 1, sticky = N+E)
        self.artist_name.config(font=('castellar', 12))
        self.song_entry = Entry(self.leftFrame, bg = 'light blue', font = 'Arial', bd = 4)
        self.song_entry.grid(row = 28, column = 2)
        self.artist_entry = Entry(self.leftFrame, bg = 'light blue', font = 'Arial', bd = 4)
        self.artist_entry.grid(row = 30, column = 2)

        # initialize random checkbox
        self.varRand = IntVar(False)
        self.checkboxRandom = Checkbutton(self.leftFrame, text='Random songs', variable=self.varRand,
                                activebackground='light green')
        self.checkboxRandom.grid(column = 3, row = 13, sticky = E)
        self.checkboxRandom.config(font=('arial', 11))

        # for spotify crawling
        self.client_credentials_manager = SpotifyClientCredentials(client_id='c90e60e8ffa54b409e84d8e8c55b7ad2',
                                                                   client_secret='982ee7b8e5684d9e9752e88c48c22764')
        self.sp = spotipy.Spotify(client_credentials_manager=self.client_credentials_manager)
        self.countries = pd.read_csv(countries_songs, encoding='utf-8')

        self.startButoon = Button(self.leftFrame, text = 'Show graph', bg = 'light green', bd = 4, fg = 'black', command = self.start)
        self.startButoon.grid(row = 40, column = 3, sticky = N+E)
        self.startButoon.config(font =('castellar', 18))

        self.playSong = Button(self.leftFrame, text='Play song', bg='light green', bd=3, fg='black',
                                  command=self.play_song)
        self.playSong.grid(row=40, column=1, sticky=N + E)
        self.playSong.config(font=('castellar', 18))


        # initialize countries checkboxes
        r, c = 0, 0
        self.checkbox_dict = checkbox_dict
        for country in dictcountries:
            self.checkbox_dict[country] = IntVar()
            if c == 4:
                r += 1
                c = 0
            c += 1
            checkboxC = Checkbutton(self.leftFrame, text=country, variable=self.checkbox_dict[country],
                                    activebackground='light green',command = self.get_list_countries, borderwidth=3)
            checkboxC.grid(row=r, column=c, sticky=W)
            checkboxC.config(font=('arial', 11))

    # main button
    def start(self):
        fig = self.make_graph()
        song, artist = self.song_entry.get(), self.artist_entry.get()
        # new song has been inserted
        if (song or artist):
            found = self.show_track(song, artist, fig)
            if found is None:
                tkinter.messagebox.showinfo("Song doesn't exist", "couldn't find the song, sorry!")
                self.song_entry.delete(0, len(song))
                self.artist_entry.delete(0, len(artist))

        list_countries = self.get_list_countries()
        # countries buttons were pressed
        if list_countries:
            self.show_country(list_countries, fig)

        # random songs button was pressed
        if self.varRand.get():
            self.show_random_song(fig)

        # draw graph
        canvas = FigureCanvasTkAgg(fig, self.rightFrame)
        canvas.draw()
        canvas.get_tk_widget().grid(sticky=E, row = 3, column = 30)

    def make_graph(self):
        fig = Figure(figsize=(6, 5),dpi=100)
        return fig

    def play_song(self):
        song, artist = self.song_entry.get(), self.artist_entry.get()
        if (song or artist):
            ids = self.get_track_artist_id(song,artist)
            if ids:
                webbrowser.open_new('https://open.spotify.com/track/' + ids[0])
                return

        webbrowser.open_new('https://open.spotify.com/track/09CtPGIpYB4BrO8qb1RGsF')
        tkinter.messagebox.showinfo("Song doesn't exist", "couldn't find the song, sorry!"
                                                             " (by Justin Bieber ;)")
        self.song_entry.delete(0, len(song))
        self.artist_entry.delete(0, len(artist))


    def get_list_countries(self):
        # check which country was selected by user
        countries = []
        for key, value in self.checkbox_dict.items():
            if value.get():
                if key in original_countries:
                    countries.append(original_countries[key])
                else:
                    countries.append(key)
        return countries

    def get_track_artist_id(self,track, artist):
        # spotify crawling
        results = self.sp.search(q=track + " " + artist, type=['track'])
        if len(results['tracks']['items']) > 0:
            for item in results['tracks']['items']:
                if item['name'].lower() == track.lower() and item['artists'][0]['name'].lower() == artist.lower():
                    return item['id'], item['artists'][0]['id']
        return None

    def get_features(self,track_id):
        return pd.DataFrame(self.sp.audio_features(['spotify:track:' + str(track_id)])[0], index=[0])

    def get_artist_popularity(self,artist_id):
        return self.sp.artist(artist_id)['popularity']

    def normalize_and_filter(self, df):
        random_df = pd.read_csv(random_songs, encoding="utf-8")

        df['duration_ms_stand'] = np.where(df['duration_ms'] >= 10 * 60 * 1000, 10 * 60 * 1000, df['duration_ms'])
        df['duration_norm'] = (df['duration_ms_stand'] - random_df['duration_ms_stand'].min()) / (
                random_df['duration_ms_stand'].max() - random_df['duration_ms_stand'].min())

        df['loudness_stand'] = np.where(df['loudness'] <= -40, -40, df['loudness'])
        df['loudness_norm'] = (df['loudness_stand'] - random_df['loudness_stand'].min()) / (
                random_df['loudness_stand'].max() - random_df['loudness_stand'].min())

        df['tempo_norm'] = (df['tempo'] - random_df['tempo'].min()) / (
                random_df['tempo'].max() - random_df['tempo'].min())
        filtered = df[['acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'mode', 'speechiness',
                       'valence', 'duration_norm', 'loudness_norm', 'tempo_norm']
        ]
        return filtered

    def show_random_song(self,fig):
        random_df = pd.read_csv(random_songs, encoding="utf-8")[
            ['acousticness', 'danceability', 'energy', 'instrumentalness'
                , 'liveness', 'mode', 'speechiness', 'valence', 'duration_norm', 'loudness_norm', 'tempo_norm',
             'artist_popularity']]
        random_df = pd.DataFrame(random_df.mean()).transpose()
        random_df.insert(loc=0, column='group', value=['Average random songs'])
        random_df.rename(columns={'loudness_norm': 'loudness', 'tempo_norm': 'tempo', 'duration_norm': 'duration'}
                              , inplace=True)
        random_df = random_df.drop(['artist_popularity'], axis=1)
        self.create_polygon(random_df, fig, False)

    def show_track(self,track_name, artist_name, fig):
        get_track = self.get_track_artist_id(track_name, artist_name)
        if get_track is None:
            return None
        track_id, artist_id = get_track
        track_data = self.get_features(track_id)
        track_df = self.normalize_and_filter(track_data)
        track_df.insert(loc=0, column='group', value=["" + track_name + " by " + artist_name + ""])
        track_df.rename(columns={'loudness_norm': 'loudness', 'tempo_norm': 'tempo', 'duration_norm': 'duration'}
                              , inplace=True)
        self.create_polygon(track_df, fig, False)
        return 1

    def show_country(self, countries_lst, fig):
        for country in countries_lst:
            country_df = self.countries.loc[self.countries['group'] == country]
            country_df.rename(columns={'loudness_norm': 'loudness', 'tempo_norm': 'tempo', 'duration_norm': 'duration'}
                              , inplace=True)
            self.create_polygon(country_df, fig, True)

    def create_polygon(self, df, fig, is_country):
        categories = list(df)
        categories.remove('group')
        N = len(categories)
        # What will be the angle of each axis in the plot? (we divide the plot / number of variable)
        angles = [n / float(N) * 2 * pi for n in range(N)]
        angles += angles[:1]
        # Initialise the spider plot

        ax = fig.add_subplot(111, polar=True)
        # If you want the first axis to be on top:
        ax.set_theta_offset(pi / 2)
        ax.set_theta_direction(-1)
        # Draw one axe per variable + add labels labels yet
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories)
        ax.set_rlabel_position(0)

        values = df.drop(['group'], axis=1).values.flatten().tolist()
        values += values[:1]
        label = df['group'].values[0]
        if is_country:
            coun = df['group'].values[0]
            if coun in original_countries.values():
                label = "Avg Popular Song in " + list(original_countries.keys())\
                    [list(original_countries.values()).index(coun)]
            else:
                label = "Avg Popular Song in " + coun
        ax.plot(angles, values, linewidth=1, linestyle='solid', label=label)
        ax.fill(angles, values, 'b', alpha=0.1)
        ax.legend(loc = 7, bbox_to_anchor = (0.5, 0, 0.15, 0))


    def main(self):
        self.root.mainloop()


if __name__ == '__main__':
    gui = Gui(dictcountries)
    gui.main()





