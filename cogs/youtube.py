from __future__ import unicode_literals
from discord.ext import commands
import urllib.request
import urllib
import discord
from bs4 import BeautifulSoup
import youtube_dl
import asyncio
import os
import random



class Youtube(commands.Cog, name='youtube'):

    def __init__(self, bot):
        self.bot = bot
        self.voice_client = self.bot._voice_clients
        self.playing = {}


    @commands.command(name="search", aliases=['zoek'])
    async def search(self, ctx, *args):
        """
            Searches YouTube. Usage: search AMOUNT KEYWORDS
        """
        await ctx.send("Searching for {}, amount of results: {}.".format(' '.join(args[1:]), args[0]))
        for i in await self._search(args[1:], int(args[0])):
            await ctx.send(i)


    @commands.command(name="play", aliases=['queue'])
    async def play(self, ctx, *args):
        try:
            await ctx.send("Searching for {}".format(" ".join(args)))
            link = await self._search(args, 1)
            song_id = link[0].replace('https://www.youtube.com/watch?v=', '')

            song = BeautifulSoup(urllib.request.urlopen(link[0]), "lxml")
            title = song.title.string.replace('- YouTube', '')
            song = Song(song_id, title, link)

            await ctx.send("Added {} to the queue. {}".format(str(song), link[0]))
            await self._download(link[0])

            if ctx.message.author.voice is None:
                await ctx.send("You are not in a voice channel!")
                raise Exception('Not in a voice channel')
            channel = ctx.message.author.voice.channel
            guild = ctx.message.author.guild.id

            await self._add_to_queue(guild, song)

            try:
                await self._join_channel(guild, channel)
                await self._play_from_queue(guild, ctx)
            except discord.ClientException:
                pass

        except discord.ClientException as e:
             await ctx.send(e)
             print(e)

    
    @commands.command(name="stop", aliased=["disconnect"])
    async def _disconnect(self, ctx):
        await self._leave_channel(ctx.message.author.guild.id)


    @commands.command(name='queued')
    async def queued(self, ctx):
        await ctx.send(
            'Current queue: \n' +
            '\n'.join(str(x) for x in await self._get_queue(ctx.message.author.guild.id
            )))


    @commands.command(name="start")
    async def start(self, ctx):
        await self._play_from_queue(ctx.message.author.guild.id, ctx)


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
        try:
            self.voice_client[guild] = await channel.connect()
        except discord.ClientException:
            pass

    
    async def _leave_channel(self, guild):
        await self.voice_client[guild].disconnect()


    async def _set_playing_status(self, music_name):
        await self.bot.change_presence(activity=discord.Game(name=music_name))


    async def _new_audio_source(self, audio):
        src = discord.FFmpegPCMAudio(audio)
        src.read()
        return src

    async def _play_audio(self, guild, song_id):
        source = await self._new_audio_source('music/{}.webm'.format(song_id))
        try:
            self.voice_client[guild].play(source)
        except discord.ClientException as ce:
            print("Already playing audio or not connected")
        # except Exception as e:
        #     print(e)


    async def _add_to_queue(self, guild, song):
        queue = []
        try:
            queue = self.bot._queue[guild]
        except KeyError:
            self.bot._queue[guild] = queue

        self.bot._queue[guild].append(song)

    
    async def _play_from_queue(self, guild, ctx):
        try:
            queue = await self._get_queue(guild)
            await ctx.send(queue)
            if len(queue) == 0:
                raise KeyError
            song = queue[random.randint(0, len(queue) - 1)]
            await self._set_playing_status(song.title)
            await self._play_audio(guild, song.song_id)
        except discord.ClientException:
            await ctx.send("There is nothing in the queue!")

    
    async def _get_queue(self, guild):
        try:
            queue = self.bot._queue[guild]
            return queue
        except KeyError:
            return []


class Song():

    def __init__(self, song_id, title, link):
        self.song_id = song_id
        self.title = title
        self.link = link


    def __str__(self):
        return self.title


def setup(bot):
    bot.add_cog(Youtube(bot))