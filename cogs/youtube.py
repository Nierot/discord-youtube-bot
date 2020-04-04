from __future__ import unicode_literals
from discord.ext import commands
import urllib.request
import urllib
import discord
from bs4 import BeautifulSoup
import youtube_dl
import asyncio
import os



class Youtube(commands.Cog, name='youtube'):

    def __init__(self, bot):
        self.bot = bot
        self.voice_client = {}
        self.playing = {}


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
            song_id = link[0].replace('https://www.youtube.com/watch?v=', '')

            song = BeautifulSoup(urllib.request.urlopen(link[0]), "lxml")
            await self._set_playing_status(song.title.string.replace('- YouTube', ''))

            await ctx.send("Playing {}".format(link[0]))
            await self._download(link[0])

            if ctx.message.author.voice is None:
                await ctx.send("You are not in a voice channel!")
                raise Exception('Not in a voice channel')
            channel = ctx.message.author.voice.channel
            guild = ctx.message.author.guild.id

            await self._join_channel(guild, channel)
            self.playing[guild] = song_id
            #song_file = os.path
            await self._play_audio(guild, 'music/{}.webm'.format(song_id))

        except discord.ClientException:
            await ctx.send("Already playing something... please try again")
            await self._leave_channel(self.voice_client[guild].disconnect())
        # except Exception as e:
        #     await ctx.send(e)
        #     print(e)

    
    @commands.command(name="disconnect", hidden=True)
    async def disconnect(self, ctx):
        await self._leave_channel(ctx.message.author.guild.id)

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
            'extractaudio': 'True',
            'keepvideo': 'False',
            'forcefilename': 'True',
            'audio-format': 'mp3',
            'format': 'bestaudio/best',
            'outtmpl': '/music/%(id)s.%(ext)s',
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([link])


    async def _join_channel(self, guild, channel):
        self.voice_client[guild] = await channel.connect()

    
    async def _leave_channel(self, guild):
        await self.voice_client[guild].disconnect()


    async def _set_playing_status(self, music_name):
        await self.bot.change_presence(activity=discord.Game(name=music_name))


    async def _new_audio_source(self, audio):
        src = discord.FFmpegPCMAudio(audio)
        src.read()
        return src

    async def _play_audio(self, guild, audio):
        source = await self._new_audio_source(audio)
        try:
            self.voice_client[guild].play(source)
        except discord.ClientException as ce:
            print("Already playing audio or not connected")
        except Exception as e:
            print(e)


def setup(bot):
    bot.add_cog(Youtube(bot))