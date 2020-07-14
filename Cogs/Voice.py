from discord.ext import commands
import discord
import shelve
import os
import sys
sys.path.insert(0, '..' + os.path.sep)
from globalvar import global_var

# Commands related to voice chat
class Voice(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.ffmpeg_dir = os.path.join('C:', 'Program Files (x86)', 'ffmpeg', 'bin', 'ffmpeg.exe')
		self.audio_dir = os.path.join('..', 'audio', '')

	@commands.command(name='join', help='Join a voice channel', aliases=['connect'])
	async def _join(self, ctx):
		if ctx.message.author.voice:
			channel = ctx.message.author.voice.channel
			if ctx.voice_client is not None:
				return await ctx.voice_client.move_to(channel)
			await channel.connect()
		else:
			await ctx.send('You must connect to a voice channel first')


	@commands.command(name='leave', help='Leave a voice channel', aliases=['disconnect'])
	async def _leave(self, ctx):
		if ctx.message.author.voice:
			if not (guild := ctx.voice_client):
				await ctx.send('The bot hasn\'t connected to a voice channel')
			else:
				await guild.disconnect()
		else:
			await ctx.send('You must connect to a voice channel first')


	@commands.command(name='play', help='Play an audio file')
	async def _play(self, ctx, name: str):
		if not ctx.voice_client:
			return await ctx.send('The bot hasn\'t connected to a voice channel')
		name += '.mp3'
		audio_file = '%s%s' % (self.audio_dir, name)
		if os.path.exists(audio_file):
			source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(executable=self.ffmpeg_dir, source=audio_file))
			ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)
			await ctx.send('Playing %s' % name)
		else:
			await ctx.send('File not found')


	@commands.command(name='volume', help='Adjust bot\'s volume (0 - 100)')
	async def _volume(self, ctx, volume: int):
		if ctx.voice_client is None:
			return await ctx.send('The bot hasn\'t connected to a voice channel')
		ctx.voice_client.source.volume = volume / 100
		await ctx.send("Changed volume to %d" % volume)


	@commands.command(name='stop', help='Stop playing audio')
	async def _stop(self, ctx):
		ctx.voice_client.stop()


	@commands.command(name='pause', help='Pause audio')
	async def _pause(self, ctx):
		ctx.voice_client.pause()


	@commands.command(name='resume', help='Resume audio')
	async def _resume(self, ctx):
		ctx.voice_client.resume()

def setup(bot):
	bot.add_cog(Voice(bot))