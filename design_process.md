# Design Process for the Project

This is a work in progress, using parts of the [double diamond design process](https://en.wikipedia.org/wiki/Double_Diamond_(design_process_model)).

**Brief:**<br>
    Use underlying music data to help with Djing for social dancing

## Research

**Research goals:**<br>
    Find a way to extract and leverage data from songs to help in creating playlists, choosing songs over others, what order to play the songs in, etc

**Assumptions**<br>
    - it's possible to extract the information<br>
    - Choosing songs for a playlist will actually be helped by more information<br>

**Items needing clarifications**<br>
    - what information can be extracted<br>
    - what information is useful to DJs in a social dancing context<br>

### User Interviews

    Questions:
        - What makes a good set?
        - Describe process when deciding which songs should go into a playlist
        - What type of song characteristics help in choosing a song?
        - what kind of extra information would be useful to have at hand when creating a playlist for an event?

## Persona Creation: Who are we designing for ?

This project is aimed at dancers who also like to DJ for social events. They have an interest in music and DJing although it is not necessarily their main hobby. They don't have the time to slowly build an extensive music collection, listening and analysing each song over the course of several years.


## Defining the Problem

Insight statements:

    Anusha wants to DJ at parties
    Because then she won't need as many Djs
    But does not have an organised music collection or does not have an in-depth knowledge of her collection

    Anusha wants to organise her music collection
    Because she Djs at parties
    But listening to all her collection is time consuming

    Anusha wants to visualise songs
    because it might provide a quick way to decide whether they are good to be played in the same set
    But she does not have a way to do so
    

Selected Statement:

    Anusha wants to DJ at parties
    Because then she won't need as many Djs
    But does not have an organised music collection or does not have an in-depth knowledge of her collection

How might we:
 - help Anusha to understand the songs in her collection?
 - help Anusha leverage the data in her music collection?
 - help Anusha to play songs without understanding her whole music collection?
 - help Anusha to avoid playing crap songs?
 - help Anusha to understand which songs to play next?
 - help Anusha to organise her music collection?
 - help Anusha to get to know her music collection?

## Ideation

Crazy 8's - 8 ideas in 8 minutes
- Bad Ideas:

- Good ideas:

## Build a hypothesis

We believe that adding a tag and bpm columns to a UI for amateur DJs will achieve better/easier song selection
We will test this by adding the columns and using the information to DJ
We will know this statement is valid by the next party if the playlist/set contains song not usually played by the DJ.

We believe that leveraging trusted playlists to generate suggest songs for amateur DJs will achieve better song suggestions than Spotify's current algorithm
We will test this by building a suggestion model (with a UI)
We will know this statement is valid by doing a blind test: how many customs suggestions were added to the playlist vs how many spotify suggestions


## Design a prototype
