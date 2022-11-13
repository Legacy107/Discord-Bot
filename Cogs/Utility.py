import os
from discord.ext import commands


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
		await self.bot.load_extension('Cogs.%s' % extension.capitalize())
		await ctx.send('Successfully loaded %s extension' % extension)

	@commands.command(name='unload', help='Unload an extension')
	@commands.is_owner()
	async def _unload(self, ctx, extension: str):
		await self.bot.unload_extension('Cogs.%s' % extension.capitalize())
		await ctx.send('Successfully unloaded %s extension' % extension)


async def setup(bot):
	await bot.add_cog(Utility(bot))
