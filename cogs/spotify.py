from discord.ext import commands

class Spotify(commands.Cog, name='Spotify'):

    def __init__(self, bot):
        self.bot = bot

    
    @commands.command(name="yeet")
    async def yeet(self, ctx):
        await ctx.send('eee')


def setup(bot):
    bot.add_cog(Spotify(bot))