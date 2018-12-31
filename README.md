![alt text][logo]


**Please don't use this yet. It's currently being rewritten**

[logo]: https://media.discordapp.net/attachments/451356934579421184/454714142977163276/Group.png "Introducing Trackrr"
![Alt text](https://media.discordapp.net/attachments/454821463715872779/454823250585714699/Artboard.png?width=1080&height=80)
> Trackrr is a discord bot that can search through the most popular music streaming apps and provide direct link to the song, album or artist.

Trackrr supports the following top music sources:
* **Spotify**
* **Apple Music**
* **SoundCloud**
* **Amazon Music**
* **YouTube Music**
* **Deezer**
* **Google Play Music**
* **Genius**
* **Bandcamp**
* **Spinrilla**
* **MusicBrainz**
* **Tidal**
* **Last.FM**
* **Pandora**
* **Mixtape Monkey**
* **Napster**

Use Trackrr with a music bot to get the full potential!

## Preview

**Song search**

Usage: ```^search_track service songname```

For example, let's say I want to search for **Bound 2** by **Kanye West**, this is an easy command. First, you can run ```^search_track``` To list the available sources for track searching. Then, you can simply run:

```^search_track spotify Bound 2```

![uploadsong](https://i.gyazo.com/f25294332e413fc87bf7b09ac7147a3e.png)

**Album search**

Usage: ```^search_album service albumname```

For example, let's say I want to search for **KIDS SEE GHOSTS**. Trackrr makes it easy.

```^search_album spotify KIDS SEE GHOSTS```

```^search_album itunes KIDS SEE GHOSTS```

```^search_album tidal KIDS SEE GHOSTS```

![uploadsong](https://i.gyazo.com/51c92fcb0ec977cb3d8add7c5d783bb8.png)

You can also use the source ```all``` to search all sources and switch between results.

**Local search**

Usage: ```^upload_song``` + MP3 Attachment

For example, what if I want to get some info about an MP3 I have? Trackrr makes this easy!

[![4amconvos](https://i.gyazo.com/b4ac173c04bb1b47978cc9eac683b090.png)](https://soundcloud.com/4amconvos)

**Artist search**

Usage: ```^search_artist artistname```

For example, what if you want to search for **Pusha T**? Trackrr can do this too!

![artist](https://i.gyazo.com/7d33394b56834ca32dc4c5db068806fe.png)

**Top charts**

Usage: ```^charts``` ```^charts albums```

Ability to grab the latest top 100 charts (optionally albums) from Billboard.

![charts](https://i.gyazo.com/641b366d17aa12b16254e373bcf4a452.png)

**Trending**

Usage: ```^trending``` ```^trending albums```

Ability to grab the current trending songs (or optionally albums) from Genius.

![trending](https://i.gyazo.com/eb28c98c6dd17bcc554f63942db816c9.png)

**Setting default service**

Usage: ```^prefs service servicename```

For example, let's say you want to search **Deezer** by default?

![prefs](https://i.gyazo.com/a430d3fc7bac7b49a61c65cfe4a0714b.png)

**Search from a user's Spotify presence**

Usage: ```^search_playing @user```

Search the song someone is currently playing on all sources.

![searchplay](https://i.gyazo.com/fe860ee997e3c35fd02815b3ab3cad5d.png)

**Favorite Songs!**

Usage: ```^favorites``` ```^favorites #```

To favorite a song, search it on Trackrr, then react to the result message with a ❤️. Trackrr will add the song to your favorites list, which can be viewed using ```^favorites```. This list will number the tracks in order, and by doing ```^favorites #``` with a respective number, you can view a song you have favorited.

![flighttomemphis](https://cdn.discordapp.com/attachments/528057306185990175/529335349080489984/ezgif.com-video-to-gif.gif)

## What works?
* **Music search**
* **Album search**
* **Artist search**
* **Local track search**
* **Top Charts**
* **Search what a user is currently listening to**
* **Analyze the audio of Spotify songs**
* **Preferences**
* **Favorites**

Trackrr will soon support:
* **AudioMack? We still need that API key**
* **Certain VC stuff (Likely YouTube)**

This bot's DB functions only work on a Unix machine. Windows is currently not supported by Motor.

Discord support server: https://discord.gg/PZVmCYS

## This bot can be adapted to suit any needs. Just remove any discord-oriented functions.
# README.md from [https://github.com/exofeel/Trackrr](https://github.com/exofeel/Trackrr "hi exo")
