import discord
from discord.ext import commands
import os
import aiohttp
import bs4
import json
import shlex
import asyncio

class Charts(object):

    async def scrape(self):
        async def _scrape(textf):
            results = []
            soup = bs4.BeautifulSoup(textf, 'lxml')
            number_one_details = soup.find('div', class_='chart-number-one__details')
            number_one_title = number_one_details.find('div', class_='chart-number-one__title').text.strip()
            number_one_artist = number_one_details.find('div', class_='chart-number-one__artist').text.strip()
            rest_details = soup.find_all('div', class_='chart-list-item__text-wrapper')[0:19]
            results.append({'name':number_one_title, 'artist':number_one_artist})
            for result in rest_details:
                result_name = result.find('span', class_='chart-list-item__title-text').text.strip()
                result_artist = result.find('div', class_='chart-list-item__artist').text.strip()
                results.append({'name':result_name, 'artist':result_artist})
            return results
        async with aiohttp.ClientSession() as session:
            async with session.get('https://www.billboard.com/charts/hot-100') as resp:
                text = await resp.text()
        self.billboard['songs'] = await _scrape(text)
        async with aiohttp.ClientSession() as session:
            async with session.get('https://www.billboard.com/charts/billboard-200') as resp:
                text = await resp.text()
        self.billboard['albums'] = await _scrape(text)
        await asyncio.sleep(10000)

    def __init__(self, bot):
        self.bot = bot
        self.billboard = {
            'songs':[],
            'albums':[]
        }
        print('Downloading Billboard Charts')
        self.bot.loop.create_task(self.scrape())

    @commands.command(name='charts')
    @commands.cooldown(10, 4, commands.BucketType.guild)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def charts(self, ctx, type="hot"):
        if type == "albums" or type=="album":
            top_20 = self.billboard['albums']
            topAlbums = '\n'.join([f'{top_20.index(item)+1}. {item.get("artist", "N/A")} - {item.get("name", "Unknown")}' for item in top_20])

            embed = discord.Embed(title="Billboard Top Albums 📈", colour=discord.Colour(0x000000), description="You can view the full list [here](https://www.billboard.com/charts/billboard-200)")

            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/451356934579421184/453994700488048640/ACSszfGQ83cFGaagro8OKEzfnzw9gnS31pMwJwn0TQs900-mo-c-c0xffffffff-rj-k-no.png")
            embed.set_author(name="Trackrr Music Search")
            embed.set_footer(text="Trackrr Music Search | Data pulled from Billboard", icon_url="https://media.discordapp.net/attachments/452763485743349761/452763575878942720/TrackrrLogo.png")

            embed.add_field(name="Albums", value=topAlbums)

            await ctx.send(embed=embed)
        else:
            
            top_20 = self.billboard['songs']
            topSongs = '\n'.join([f'{top_20.index(item)+1}. {item.get("artist", "N/A")} - {item.get("name", "Unknown")}' for item in top_20])

            embed = discord.Embed(title="Billboard Top Songs 📈", colour=discord.Colour(0x000000), description="You can view the full list [here](https://www.billboard.com/charts/hot-100)")

            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/451356934579421184/453994700488048640/ACSszfGQ83cFGaagro8OKEzfnzw9gnS31pMwJwn0TQs900-mo-c-c0xffffffff-rj-k-no.png")
            embed.set_author(name="Trackrr Music Search")
            embed.set_footer(text="Trackrr Music Search | Data pulled from Billboard", icon_url="https://media.discordapp.net/attachments/452763485743349761/452763575878942720/TrackrrLogo.png")

            embed.add_field(name="Songs", value=topSongs)

            await ctx.send(embed=embed)

    @commands.command(name='trending')
    @commands.cooldown(10, 4, commands.BucketType.guild)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def trending(self, ctx, type="hot"):
        async with ctx.channel.typing():
            async with aiohttp.ClientSession() as session:
                if type == "albums":
                    async with session.get('https://genius.com/api/albums/chart?page=1&per_page=20&time_period=day') as resp:
                        resp_json = await resp.json()
                    topAlbums_raw = resp_json.get('response', {}).get('chart_items', [])
                    topAlbums = '\n'.join([f'{topAlbums_raw.index(item)+1}. {item.get("item", {}).get("artist", {}).get("name", "Unknown")} - {item.get("item", {}).get("name", "Unknown")}' for item in topAlbums_raw])

                    embed = discord.Embed(title="Genius Trending Albums 🔥", colour=discord.Colour(0xffff00), description="You can view the full list [here](https://www.genius.com/)")

                    embed.set_thumbnail(url="https://media.discordapp.net/attachments/454819758072922122/457647499893800962/TrackrrGenius.png?width=527&height=527")
                    embed.set_author(name="Trackrr Music Search")
                    embed.set_footer(text="Trackrr Music Search | Data pulled from Genius", icon_url="https://media.discordapp.net/attachments/452763485743349761/452763575878942720/TrackrrLogo.png")

                    embed.add_field(name="Albums", value=topAlbums)

                    await ctx.send(embed=embed)
                else:
                    async with session.get('https://genius.com/api/songs/chart?page=1&per_page=20&time_period=day') as resp:
                        resp_json = await resp.json()
                    topSongs_raw = resp_json.get('response', {}).get('chart_items', [])
                    topSongs = '\n'.join([f'{topSongs_raw.index(item)+1}. {item.get("item", {}).get("primary_artist", {}).get("name", "Unknown")} - {item.get("item", {}).get("title", "Unknown")}' for item in topSongs_raw])

                    embed = discord.Embed(title="Genius Trending Songs 🔥", colour=discord.Colour(0xffff00), description="You can view the full list [here](https://www.genius.com/)")

                    embed.set_thumbnail(url="https://media.discordapp.net/attachments/454819758072922122/457647499893800962/TrackrrGenius.png?width=527&height=527")
                    embed.set_author(name="Trackrr Music Search")
                    embed.set_footer(text="Trackrr Music Search | Data pulled from Genius", icon_url="https://media.discordapp.net/attachments/452763485743349761/452763575878942720/TrackrrLogo.png")

                    embed.add_field(name="Songs", value=topSongs)

                    await ctx.send(embed=embed)

    @commands.command(name='viral')
    @commands.cooldown(10, 4, commands.BucketType.guild)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def viral(self, ctx):
        async with ctx.channel.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get('https://spotifycharts.com/viral/us/daily/latest/download') as resp:
                    resp_text = await resp.text()
                top_20 = []
                for line in resp_text.splitlines()[1:20]:
                    m = shlex.shlex(line, posix=True)
                    m.whitespace += ','
                    m.whitespace_split = True
                    m = list(m)
                    top_20.append({'artist': m[2], 'place': m[0], 'name': m[1]})
                topSongs = '\n'.join([f'{item.get("place")}. {item.get("artist", "N/A")} - {item.get("name", "Unknown")}' for item in top_20])

                embed = discord.Embed(title="Spotify Viral Songs 🖥", colour=discord.Colour(0x84bd00), description="You can view the full list [here](https://www.spotifycharts.com/viral/us/daily/latest)")

                embed.set_thumbnail(url="https://images-eu.ssl-images-amazon.com/images/I/51rttY7a%2B9L.png")
                embed.set_author(name="Trackrr Music Search")
                embed.set_footer(text="Trackrr Music Search | Data pulled from SpotifyCharts", icon_url="https://media.discordapp.net/attachments/452763485743349761/452763575878942720/TrackrrLogo.png")

                embed.add_field(name="Songs", value=topSongs)

                await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Charts(bot))