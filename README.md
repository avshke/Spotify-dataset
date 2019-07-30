# spotify-dataset
Is it possible to predict the popularity of a song solely through its musical characteristics? 
And if so, how? Do popular songs in different countries have different musical characteristics? 
And what are they? In this project we tried Approach this question in different ways, 
and look at the musical characteristics of a song in a new perspective.

take 1- 
To access the questions that interest us, we searched for suitable data. 
We wanted the data to contain a lot of songs, their musical characteristics, basic details about the performing artist, 
and of course, measures of how popular the song is in different countries and in general. 
We chose to combine data from three different sources:
1. Spotify
2. Google Trends
3. Youtube
Bottom line, there seemed to be a mismatch between popularity scores in youTube and Spoyify.
By clustering we tried to classify popular groups but without success.
That is why we have not been able to train a model to predict what we need.

take 2-
In order to counteract the problems that stem from the combination of Spotify and YouTube, 
and from working with a lot of songs that are not very popular at all, 
we decided to work with Data Set describing the 200 most popular songs each day in 2017 in 50 different countries.
We have found differences in take 1 clustering but have not yet been able to train a proper model.


The obvious lack of success of the models brought us back to the fundamental question - 
"Can a song's popularity be predicted only by its musical characteristics?"
We argue that, for various reasons, songs with similar musical properties can be found, 
whose popularity is significantly different.

Gui-
We chose a radar graph because it allows you to examine all of the musical properties at once, 
for example, to look at a particular song relative to the average popular song in a country, 
compare a song to "average song", or compare the average popular song in different countries. 
Using the radar graph can visually illustrate differences in musical preference between different countries.


