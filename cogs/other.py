import discord
from discord.ext import commands
import cogs.mods.genius as genius

class Lyrics:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='lyrics')
    async def lyrics(self, ctx, *, song_name):
        async with ctx.channel.typing():
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
                embed = discord.Embed(title=hit.get('title', 'Trackrr') + ' by ' + hit.get('primary_artist', {}).get('name', 'N/A') + ' <:genius:528067300520362014>', description=segment, url=hit.get("url", "https://genius.com/"))
                embed.set_thumbnail(url=hit.get('header_image_url', 'https://github.com/exofeel/Trackrr/blob/master/assets/UnknownCoverArt.png?raw=true'))
                embed.set_footer(text=f"Trackrr Music Search | Data pulled from Genius", icon_url="https://media.discordapp.net/attachments/452763485743349761/452763575878942720/TrackrrLogo.png")
                await ctx.send(embed=embed)

class Producers:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='producer_tag', aliases=['prod_by', 'prodby', 'producertag', 'producer', 'producers', 'producer_tags', 'producertags', 'prod', 'prods'])
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
                producer = {'name':b.text, 'tags':[]}
                # print('----')
                for tag in b.next_siblings:
                    # print('[' + getattr(tag, 'text', '').strip() + ']', prev_elem)
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

            final_producer = {'name':'Unknown', 'tags':['N/A']}
            for producer in producers:
                if producer_name.lower() in producer.get('name', '').lower():
                    final_producer = producer
                    break
            embed = discord.Embed(title=final_producer['name'].strip(), description='*' + '\n'.join(final_producer['tags']) + '*')
            embed.set_footer(text=f"Trackrr Music Search | Data pulled from Genius", icon_url="https://media.discordapp.net/attachments/452763485743349761/452763575878942720/TrackrrLogo.png")
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Lyrics(bot))
    bot.add_cog(Producers(bot))