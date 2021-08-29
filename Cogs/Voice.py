from dotenv import load_dotenv, find_dotenv
import functools
import json
import os
import random
import re
import sys

import discord
from discord.ext import commands
from discord.utils import escape_mentions
from gtts import gTTS, lang
from io import BytesIO
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
from globalvar.global_var import spotify_albums_dir, tts_dir, emoji


class Spotify:
	def __init__(self):
		ENV_FILE = find_dotenv()
		if ENV_FILE:
			load_dotenv(ENV_FILE)
		CID = os.getenv('SPOTIFY_CID')
		SECRET = os.getenv('SPOTIFY_SECRET')

		client_credentials_manager = SpotifyClientCredentials(client_id=CID, client_secret=SECRET)
		self.Client = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

		with open(spotify_albums_dir) as albums_file:
			self.albums = json.load(albums_file)

	def validate_option(self, option):
		return option in self.albums

	def get_playlist_tracks(self, option):
		if type(self.albums[option]) is list:
			playlist_id = random.choice(self.albums[option])
		else:
			playlist_id = self.albums[option]

		total_tracks = self.Client.playlist(playlist_id, fields='tracks')['tracks']['total']
		offset = random.randint(0, max(0, total_tracks-10))
		data = self.Client.playlist_tracks(playlist_id, limit=10, offset=offset)['items']
		data = list(map(lambda item: item['track'], data))
		data = list(map(self.clear_data, data))
		random.shuffle(data)
		return data

	def get_track_generator(self, option):
		tracks = self.get_playlist_tracks(option)
		for track in tracks:
			yield track

	@staticmethod
	def clear_data(item):
		return {
			'artist': functools.reduce(lambda names, artist: names + (' x ' if names else '') + artist['name'], item['artists'], ''),
			'album': item['album']['name'] if item['album']['album_type'] != 'single' else 'single',
			'image_url': item['album']['images'][-1]['url'],
			'name': item['name'],
			'popularity': item['popularity'],
			'track_url': item['external_urls']['spotify'],
		}

# Commands related to voice chat
class Voice(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.audio_dir = os.path.join('..', 'audio', '')
		self.spotify = Spotify()
		self.track_generator = {}

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
			source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(source=audio_file))
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


	@commands.group(help='Song generator')
	async def song(self, ctx):
		pass


	def get_track(self, option):
		generator = self.track_generator.setdefault(option, self.spotify.get_track_generator(option))
		try:
			track = next(generator)
		except:
			generator = self.track_generator[option] = self.spotify.get_track_generator(option)
			track = next(generator)
		return track


	@song.command(name='pick', help='Pick a random song. Syntax: >song pick <option (required)>')
	async def _pick(self, ctx, *, arg):
		option = arg

		if not self.spotify.validate_option(option):
			return await ctx.send('Invalid option')

		track = self.get_track(option)

		music_note = emoji['music']
		embed = discord.Embed(title='%s %s %s' % (music_note, track['name'], music_note), description=track['artist'], url=track['track_url'], color=discord.Color.teal())
		embed.set_thumbnail(url=track['image_url'])
		if track['album'] != 'single':
			embed.set_footer(text='from album: %s' % track['album'])
		await ctx.send(embed=embed)


	# @song.command(name='play', help='Play a random song. Syntax: >song play <music bot\'s prefix> <option (required)>')
	# async def _play_song(self, ctx, prefix, *, arg):
	# 	option = arg
		
	# 	if not self.spotify.validate_option(option):
	# 		return await ctx.send('Invalid option')
		
	# 	track = self.get_track(option)

	# 	await self._join(ctx)
	# 	await ctx.send(prefix + 'play ' + track['name'])
	# 	#await self._leave(ctx)


	@song.command(name='option', help='Show all options in ur DM')
	async def _option(self, ctx):
		options = '`| '
		for option in self.spotify.albums.keys():
			options += option + ' | '
		options += '`'
		await ctx.message.author.send(options)


	@commands.command(name='say', help='Convert text to speech. Syntax: >say <lang (optional, default: en)> <text>', aliases=['tts'])
	async def _say(self, ctx, *, arg):
		# mp3_fp = BytesIO()
		# tts = gTTS(arg, lang='en')
		# tts.write_to_fp(mp3_fp)
		# mp3_fp.seek(0)

		# Get language option
		langs = lang.tts_langs().keys()
		option = arg.split()[0]
		if option in langs:
			arg = arg[len(option) + 1:]
		else:
			option = 'en'

		# Parse mentions
		arg = escape_mentions(arg)
		pattern = '<[^<>]*>'
		users = ctx.message.mentions
		for user in users:
			arg = re.sub(pattern, user.display_name, arg, 1)

		gTTS(arg, lang=option).save(tts_dir)

		source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(source=tts_dir))
		ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)


	@commands.command(name='langs', help='Show all supported tts languages', aliases=['lang'])
	async def _langs(self, ctx):
		options = '`| '
		langs = lang.tts_langs()
		for lang_ in langs.keys():
			options += lang_ + ' | '
		options += '`'
		await ctx.message.author.send(options)


	@_play.before_invoke
	@_say.before_invoke
	async def ensure_voice(self, ctx):
		if ctx.voice_client is None:
			if ctx.author.voice:
				await ctx.author.voice.channel.connect()
			else:
				await ctx.send("You are not connected to a voice channel")
				raise commands.CommandError("Author not connected to a voice channel")
		elif ctx.voice_client.is_playing():
			await ctx.send("The bot is playing. Use >hm stop to force stop")
			raise commands.CommandError("Bot is playing")


def setup(bot):
	bot.add_cog(Voice(bot))


if __name__ == "__main__":
	# Testing
	spotify = Spotify()
	spotify.get_playlist_tracks('acoustic')
