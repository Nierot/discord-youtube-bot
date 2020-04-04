from discord.ext import commands
import urllib.request
import urllib
import discord
from bs4 import BeautifulSoup
import youtube_dl
import asyncio


class Youtube(commands.Cog, name='youtube'):

    def __init__(self, bot):
        self.bot = bot
        self.voice_client = None


    @commands.command(name="search", aliases=['zoek', 'queue'])
    async def search(self, ctx, *args):
        """
            Searches YouTube. Usage: search AMOUNT KEYWORDS
        """
        await ctx.send("Searching for {}, amount of results: {}.".format(' '.join(args[1:]), args[0]))
        for i in await self._search(args[1:], int(args[0])):
            await ctx.send(i)


    @commands.command(name="play")
    async def play(self, ctx, *args):
        try:
            await ctx.send("Searching for {}".format(" ".join(args)))
            link = await self._search(args, 1)

            song = BeautifulSoup(urllib.request.urlopen(link[0]), "lxml")
            await self._set_playing_status(song.title.string.replace('- YouTube', ''))

            await ctx.send("Playing {}".format(link[0]))
            await self._download(link[0])

            channel = ctx.message.author.voice.channel
            if channel is None:
                ctx.send("You are not in a voice channel!")

            await self._join_channel(channel)
            await self._play_audio('CHRISTOPHER BOWES AND HIS PLATE OF BEANS - Midnight Breakfast _ Napalm Records-HR6kOHccYRY.webm')

            #audio_source = discord.FFmpegPCMAudio('CHRISTOPHER BOWES AND HIS PLATE OF BEANS - Midnight Breakfast _ Napalm Records-HR6kOHccYRY.webm')
        except Exception as e:
            await ctx.send(e)

    
    @commands.command(name="disconnect", hidden=True)
    async def disconnect(self, ctx):
        await self._leave_channel()

    async def _search(self, keyword: [], amount):
        keyword = ' '.join(keyword)
        query = urllib.parse.quote(keyword)
        url = "https://www.youtube.com/results?search_query=" + query
        response = urllib.request.urlopen(url)
        html = response.read()
        soup = BeautifulSoup(html, 'html.parser')
        i = 0
        res = []
        for vid in soup.findAll(attrs={'class':'yt-uix-tile-link'}):
            if not vid['href'].startswith("https://googleads.g.doubleclick.net/") and i < amount:
                i += 1
                if 'watch?' not in vid['href']:
                    i -= 1
                    continue
                res.append('https://www.youtube.com' + vid['href'])
        return res


    async def _download(self, link):
        ydl_opts = {
            'extractaudio': True,
            'keepvideo': False,
            'format': 'bestaudio/best',
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([link])


    async def _join_channel(self, channel):
        self.voice_client = await channel.connect()

    
    async def _leave_channel(self):
        await self.voice_client.disconnect()


    async def _set_playing_status(self, music_name):
        await self.bot.change_presence(activity=discord.Game(name=music_name))


    async def _new_audio_source(self, audio):
        src = discord.FFmpegPCMAudio(audio)
        src.read()
        return src

    async def _play_audio(self, audio):
        source = self._new_audio_source(audio)
        try:
            self.voice_client.play(source)
        except discord.ClientException as ce:
            print("Already playing audio or not connected")
        except Exception as e:
            print(e)


def setup(bot):
    bot.add_cog(Youtube(bot))