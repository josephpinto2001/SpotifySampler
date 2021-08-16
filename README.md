# SpotifySampler

## Introduction

This Spotify Sampling tool pulls data from Whosampled.com and curates a custom playlist of all samples contained in a given song.

## Installation

### Prerequisites

 - [Chrome Webdriver](https://sites.google.com/a/chromium.org/chromedriver/downloads)
 - [Register for a Spotify App](https://developer.spotify.com/dashboard/login)
 
### Setup

Once registered for a Spotify App, add a Redirect URI to the Application settings. Before running the script, store the `SPOTIPY_REDIRECT_URI`,
`SPOTIFY_CLIENT_ID`, and `SPOTIFY_CLIENT_SECRET` in environment variables. This can be achieved using a .env file as follows:

```
SPOTIPY_CLIENT_ID="<ClIENT ID>"
SPOTIPY_CLIENT_SECRET="<CLIENT SECRET>"
SPOTIPY_REDIRECT_URI="<REDIRECT URI>"
```

Finally, before running ensure to update the `chromedriver_PATH` variable on line 16 of [scraper.py](scraper.py) to your local
path to the Chrome webdriver

## Usage

first enter the venv with
```
source env/bin/activate
```
Then run the script:

```
python scraper.py <Spotify Username> "<Song Title>" "<Song Artist>"
```

Note that a "Spotify Username" is the numerical Username associated with your personal account,
which can be found [here](https://www.spotify.com/account/overview/)
