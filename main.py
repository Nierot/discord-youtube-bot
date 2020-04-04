from discord.ext import commands
import discord
import secrets
import aiohttp

class Bot:

    prefix = '!'
    description = 'Test bot'
    extensions = ['cogs.spotify', 'cogs.youtube', 'cogs.admin']

    def __init__(self):
        self.token = secrets.TOKEN
        self.bot = commands.Bot(command_prefix=self.prefix, description=self.description)

    
    def load_extensions(self):
        try:
            for ext in self.extensions:
                self.bot.load_extension(ext)
        except Exception as e:
            print(e)


    def reload_extensions(self):
        try:
            for ext in self.extensions:
                self.bot.reload_extension(ext)
        except Exception as e:
            print(e)


    def run(self):
        self.load_extensions()
        
        @self.bot.event
        async def on_ready():
            self.bot._session = aiohttp.ClientSession()
            print(self.bot.user.name)
            print(self.bot.user.id)
            print(discord.utils.oauth_url(self.bot.user.id))
        
        self.bot.run(self.token)


if __name__ == "__main__":
    bot = Bot()
    bot.run()