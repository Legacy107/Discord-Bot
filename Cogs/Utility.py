from discord.ext import commands
import discord
import os
import sys
sys.path.insert(0, '..' + os.path.sep)
from globalvar import global_var

# Utility commands
class Utility(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.data_dir = os.path.join('..', 'data', 'data')	# ..\data

	@commands.command(name='ping', help='Ping the bot')
	async def _ping(self, ctx):
	    await ctx.send('pong')

	@commands.command(name='load', help='Load an extension')
	@commands.is_owner()
	async def _load(self, ctx, extension: str):
		self.bot.load_extension('Cogs.%s' % extension.capitalize())
		await ctx.send('Successfully loaded %s extension' % extension)

	@commands.command(name='unload', help='Unload an extension')
	@commands.is_owner()
	async def _unload(self, ctx, extension: str):
		self.bot.unload_extension('Cogs.%s' % extension.capitalize())
		await ctx.send('Successfully unloaded %s extension' % extension)


def setup(bot):
	bot.add_cog(Utility(bot))
