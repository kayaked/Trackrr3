from datetime import datetime

import motor.motor_asyncio
import discord
from discord.ext import commands

import cogs.mods.genius as genius
import cogs.mods.spotify as spotify 

client = motor.motor_asyncio.AsyncIOMotorClient()
db = client['Trackrr']


class AudioInfomation:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='analyze', aliases=['analyse', 'advanced_info', 'adv_info'])
    async def analyze(self, ctx):


        # Discord User Information
        user_activity = ctx.author.activity

        if isinstance(user_activity, discord.Spotify) is True:



            # Discord provided Track Information
            track_name = user_activity.title
            track_cover_art = user_activity.album_cover_url

            searching_message = await ctx.send('🔍 Analyzing {}'.format(track_name))



            track_info_get = await spotify.analyze_song(user_activity.track_id)

            # Create Local Dict for embed
            track_info = {}


            for key, value in track_info_get.items():

                embed_values = [
                    "duration_ms", "key", "mode", "time_signature", "danceability",
                    "energy", "instrumentalness", "liveness", "speechiness", "loudness",
                    "valence", "tempo"
                ]

                if key in embed_values:

                    # Add to Dict
                    track_info[key] = value

                else:
                    pass

            embed = discord.Embed(title="Audio Analysis", description="Here is detailed information about the track  " + track_name)
            embed.set_thumbnail(url=track_cover_art)

            # I'm gonna try somethin crazy

            for key, value in track_info.items():

                values_ignore = [
                    'analysis_url', 
                    'track_href', 
                    'uri', 
                    'type',
                ]

                value_aliases = {

                    "duration_ms": "Duration (in ms)",
                    "key": "Key",
                    "mode": "Mode",
                    "time_signature": "Time Signature",
                    "danceability": "Danceability",
                    "energy": "Energy",
                    "instrumentalness": "Instrumentalness",
                    "liveness": "Liveness",
                    "speechiness": "Speechiness",
                    "loudness": "Loudness",
                    "valence": "Vibe",
                    "tempo": "BPM"

                }

                values_to_round = [

                    "danceability",
                    "energy",
                    "instrumentalness",
                    "liveness",
                    "speechiness",
                    "valence"

                ]


                if key in values_ignore:
                    pass

                else:
                    key_formatted = value_aliases.get(key, key)

                    # Round BPM

                    if key in values_to_round:

                        val_readable = value * 100
                        value = round(val_readable)

                    else:
                        pass


                    # Pitch Classes for Keys
                    pitch_classes = {

                        -1: "No Key detected.",
                        0: "C",
                        1: "D♭",
                        2: "D",
                        3: "E♭",
                        4: "E",
                        5: "F",
                        6: "G♭",
                        7: "G",
                        8: "A♭",
                        9: "A",
                        10: "B♭",
                        11: "B"
                    }


                    modes = {

                        -1: "No Mode Detected",
                        0: "Minor",
                        1: "Major"
                    }

                    ## Custom Funcs
                    def bpm(tempo):
                        return round(tempo)

                    if key_formatted == "BPM":
                        value = bpm(value)

                    elif key_formatted == "Loudness":
                        decibel = round(value)

                        value = "{} dB".format(decibel)

                    elif key_formatted == "Majorode":
                        try:
                            value = modes.get(value, value)
                        except Exception:
                            pass

                    elif key_formatted == "Key":
                        try:
                            value = pitch_classes.get(value, value)
                        except Exception:
                            pass
        
                    else:
                        pass
                    embed.add_field(name=value_aliases.get(key, key), value=value, inline=True)

            embed.add_field(name="Have no idea what these mean?", value="[Learn more about these values and what they mean](https://www.reddit.com/user/exofeel/comments/ab2aw3/trackrr_what_do_the_values_mean/)")
            
            await ctx.send(embed=embed)
            await searching_message.delete()
        else:
            await ctx.send('not listening to spotify.')


class Lyrics:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='yandhi')
    async def yandhi(self, ctx):

        # release YANDHI kanye
        before_date = datetime(2018, 9, 28, 0, 0)
        after_date = datetime.now()

        def get_days_passed(before, after):
            d1 = before.date()
            d2 = after.date()
            return abs(d1 - d2).days

        number_of_days = get_days_passed(before_date, after_date)
        embed = discord.Embed(
            title="It has been {} days since YANDHI's announcement date.".format(number_of_days),
            description="Trust the process."
        )

        await ctx.send(embed=embed)

    @commands.command(name='bobby')
    async def bobby(self, ctx):
        # free bobby shmurda

        after_date = datetime(2020, 12, 1, 0, 0)
        before_date = datetime.now()

        def get_days_passed(before, after):
            d1 = before.date()
            d2 = after.date()
            return abs(d1 - d2).days

        number_of_days = get_days_passed(before_date, after_date)
        embed = discord.Embed(title="{} days until Bobby Shmurda is FREE! 🙏".format(number_of_days))
        await ctx.send(embed=embed)

    @commands.command(name='lyrics')
    @commands.cooldown(3, 5, commands.BucketType.guild)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def lyrics(self, ctx, *, song_name):
        perms = ctx.channel.permissions_for(ctx.author)
        if getattr(perms, 'manage_messages', False):
            channel = ctx.channel
        else:
            channel = ctx.author
        async with channel.typing():

            lyrics, hit = await genius.get_song_lyrics(song_name)
            lyrics = getattr(lyrics, 'text', 'Lyrics not found.').strip('\n')
            lyrics_split = []
            lyrics_rawsplit = lyrics.split('\n')
            lyrics_segment = []

            for line in range(0, len(lyrics_rawsplit)):
                if ('\n'.join(lyrics_segment) + '\n' + lyrics_rawsplit[line]).__len__() <= 2000:
                    lyrics_segment.append(lyrics_rawsplit[line])
                else:
                    lyrics_split.append('\n'.join(lyrics_segment))
                    lyrics_segment = [lyrics_rawsplit[line]]
                if line == len(lyrics_rawsplit)-1:
                    lyrics_split.append('\n'.join(lyrics_segment))
                    break

            lyrics_split = [seg[:2000].strip() for seg in lyrics_split]

            if lyrics_split.__len__() > 3:
                lyrics_split = lyrics_split[:3]
                lyrics_split[-1] += f'[...]({hit.get("url", "")})'
                lyrics_split[-1] = lyrics_split[-1][:2048]

            for segment in lyrics_split:

                embed = discord.Embed(
                    title=hit.get('title', 'Trackrr') + ' by ' + hit.get('primary_artist', {}).get('name', 'N/A') + ' <:genius:528067300520362014>',
                    description=segment,
                    url=hit.get("url", "https://genius.com/")
                )

                embed.set_thumbnail(
                    url=hit.get('header_image_url', 'https://github.com/exofeel/Trackrr/blob/master/assets/UnknownCoverArt.png?raw=true')
                )

                embed.set_footer(
                    text=f"Trackrr Music Search | Data pulled from Genius",
                    icon_url="https://media.discordapp.net/attachments/452763485743349761/452763575878942720/TrackrrLogo.png"
                )
                await channel.send(embed=embed)


class Producers:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='producer_tag', aliases=['prod_by', 'prodby', 'producertag', 'producer', 'producers', 'producer_tags', 'producertags', 'prod', 'prods'])
    @commands.cooldown(10, 5, commands.BucketType.guild)
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def producer_tag(self, ctx, *, producer_name):
        async with ctx.channel.typing():
            lyrics, hit = await genius.get_song_lyrics('Rap Genius Producer Tags')
            hit
            producers = []
            prev_elem = 'b'

            # Scrapes the producer tags from Rap Genius's Producer tag library.
            # Since this page is made with user contributions (AND currently LOCKED from editing), it has many mistakes in its formatting.
            # It would be nice if I could do it all with one simple double line break split, but to improve accuracy I am not going to.
            # Report any bugs to Yak#7474 ASAP. ty for using trackrr!

            for b in lyrics.find_all('b'):
                producer = {'name': b.text, 'tags': []}
                for tag in b.next_siblings:
                    if tag.name == "b" and prev_elem != 'b':
                        prev_elem = 'b'
                        break
                    elif tag.name == 'b' and prev_elem == 'b':
                        producer['name'] = producer.get('name', '') + tag.text
                    elif tag.name == 'a' and getattr(tag, 'get', {}.get)('class', [1])[0] == 'referent':
                        if '\n' in tag.text:
                            producer['tags'] += tag.text.strip().split('\n')
                        else:
                            producer['tags'].append(tag.text.strip())
                    prev_elem = tag.name if tag.name else prev_elem
                if producer.get('tags'):
                    producers.append(producer)

            final_producer = {'name': 'Unknown', 'tags': ['N/A']}
            for producer in producers:
                if producer_name.lower() in producer.get('name', '').lower():
                    final_producer = producer
                    break
            embed = discord.Embed(title=final_producer['name'].strip(), description='*' + '\n'.join(final_producer['tags']) + '*')
            embed.set_footer(
                text=f"Trackrr Music Search | Data pulled from Genius", 
                icon_url="https://media.discordapp.net/attachments/452763485743349761/452763575878942720/TrackrrLogo.png"
            )

            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Lyrics(bot))
    bot.add_cog(Producers(bot))
    bot.add_cog(AudioInfomation(bot))
