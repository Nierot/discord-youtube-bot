from discord.ext import commands

class Admin(commands.Cog, name='Helper'):

    extensions = ['cogs.spotify', 'cogs.admin', 'cogs.youtube']

    def __init__(self, bot):
        self.bot = bot


    @commands.command(name='reload', hidden=True)
    async def _reload(self, ctx):
        self.reload(ctx)


    async def reload(self, ctx):
        try:
            for ext in self.extensions:
                self.bot.reload_extension(ext)
                await ctx.send("Reloading... {}".format(ext.replace('cogs.', '')))
                print("--------- {}".format(ext.replace('cogs.', '')))
                print()
        except Exception as e:
            await ctx.send(e)

    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.content.lower() == 'r':
            await self.reload(message.channel)


def setup(bot):
    bot.add_cog(Admin(bot))