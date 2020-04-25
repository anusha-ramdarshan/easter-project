# easter-project

This is a work in progress, using parts of the [double diamond design process](https://en.wikipedia.org/wiki/Double_Diamond_(design_process_model)).


For details of the design process, refer to [design_process.md](design_process.md)

# Getting Started

## Install dependencies

    pipenv install

## Make a .env config file from the template

    cp .env.example .env

## Make a spotify app and configure it

* Go to https://developer.spotify.com/dashboard/applications and click `CREATE A CLIENT ID`.
* Fill in the form to create a new app.
* Go into your newly created app
  * Copy the relevant values into SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET.
  * Click `EDIT SETTINGS`
    * Copy the value from `SPOTIPY_REDIRECT_URI` into `Redirect URIs`, and click `ADD`
      * (If you get a white error page from spotify saying `INVALID_CLIENT: Invalid redirect URI` in a later page, you forgot to do this step)


## Run the Plotly Dash app

    pipenv run python easter_project/app.py

It should pop up an authorisation page.

Once you have authorized your app, it should print out a message in the terminal saying where the dashboard is hosted. Go there to view the dashboard.
