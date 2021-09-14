# Spotify playlist generator

## Project description
This project is used for retrieving tracks from certain VK music groups and automatically create a daily Spotify playlist.

For now I get tracks from 5 different groups where each of them has its own post structure. And that is why when you want
to add a new VK group that should be processed, first you need to determine its structure and write corresponding code.
This part is what makes this project is kind of hard to use for your own public.

But when you are done with this part, you can finally enjoy listening to music without spending extra time manually 
switching between different VK tabs and searching for the same liked VK tracks in Spotify


## Solution
Spotify and VK provide good and clear APIs which were used in the project.


## How to run
First, you need to have:
1) VK API key
2) Your Spotify user id
3) Your Spotify app token

and add those values to environment variables

Second, when you are all set, run this line of code:

```python main.py```
