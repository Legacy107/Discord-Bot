from dotenv import load_dotenv, find_dotenv
import inspect
import os
import re
import sys

import discord
from discord.ext import commands
from PyDictionary import PyDictionary
from random_word import RandomWords, Wordnik

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
from globalvar.global_var import emoji

# Load config from env
ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)
WORDNIK_API_KEY = os.getenv('WORDNIK_API_KEY')

English_dictionary = PyDictionary()
random_word = Wordnik(api_key=WORDNIK_API_KEY)
RE_invalid_word = re.compile('\d|\'')	# contains digits or symbols except for hyphen


def gen_rand_word():
	try:
		word = random_word.get_random_word(hasDictionaryDef="true", minCorpusCount=1000, minLength=4).lower()
		if RE_invalid_word.search(word):
			print('Word contains digits or symbols')
			return gen_rand_word()
		meaning = English_dictionary.meaning(word)
		if meaning:
			return word, meaning
		return gen_rand_word()
	except:
		print('Fail to gen_rand_word')
		return gen_rand_word()


class Hangman_Game:
	state = ['\\_\\_\\_\\_\\_\\_\n*​ ​*|\n*​ ​*|\n*​ ​*|\nᗑ*​ ​ ​*███',
			 '\\_\\_\\_\\_\\_\\_\n*​ ​*|*​ ​ ​ ​ ​ ​ ​*ό\n*​ ​*|\n*​ ​*|\nᗑ*​ ​ ​*███',
			 '\\_\\_\\_\\_\\_\\_\n*​ ​*|*​ ​ ​ ​ ​ ​ ​*ό\n*​ ​*|*​ ​ ​ ​ ​ ​ ​*|\n*​ ​*|\nᗑ*​ ​ ​*███',
			 '\\_\\_\\_\\_\\_\\_\n*​ ​*|*​ ​ ​ ​ ​ ​ ​*ό\n*​ ​*|*​ ​ ​ ​ ​*/|\n*​ ​*|\nᗑ*​ ​ ​*███',
			 '\\_\\_\\_\\_\\_\\_\n*​ ​*|*​ ​ ​ ​ ​ ​ ​*ό\n*​ ​*|*​ ​ ​ ​ ​*/|\\\n*​ ​*|\nᗑ*​ ​ ​*███',
			 '\\_\\_\\_\\_\\_\\_\n*​ ​*|*​ ​ ​ ​ ​ ​ ​*ό\n*​ ​*|*​ ​ ​ ​ ​*/|\\\n*​ ​*|*​ ​ ​ ​ ​*/\nᗑ*​ ​ ​*███',
			 '\\_\\_\\_\\_\\_\\_\n*​ ​*|*​ ​ ​ ​ ​ ​ ​*ό\n*​ ​*|*​ ​ ​ ​ ​*/|\\\n*​ ​*|*​ ​ ​ ​ ​*/ \\\nᗑ*​ ​ ​*███',
			 '\\_\\_\\_\\_\\_\\_\n*​ ​*|*​ ​ ​*⊛|\n*​ ​*|*​ ​ ​ ​ ​*/|\\\n*​ ​*|*​ ​ ​ ​ ​*/ \\\nᗑ']
	thumbnail = 'https://cdn.discordapp.com/attachments/706438294245736469/707190336019103824/hangman32.png'
	is_processing = False

	def __init__(self):
		self.status = False
		self.word, meaning = gen_rand_word()
		self.word_length = len(self.word) - self.word.count('-')
		print(self.word)

		self.guessed_word = '_' * len(self.word)
		if len(self.word) != self.word_length:
			self.reveal('-')

		self.meaning = [f'**Meaning of \"{self.word}\":**', '']
		for word_type, mean in meaning.items():
			partial_mean = mean[0]
			self.meaning[1] += '**⠂%s:** %s\n' % (word_type, partial_mean)

		self.guess_cnt = 0
		self.max_guess = 6
		self.letter_count = [0] * 26
		for letter in self.word:
			if (index := self.get_letter_id(letter)) < 26 and index >= 0:
				self.letter_count[index] += 1

	@staticmethod
	def verify_guess(word):
		return all(text.isalpha() for text in word.split('-'))

	@staticmethod
	def get_letter_id(letter):
		return ord(letter) - ord('a')

	@staticmethod
	async def add_reactions(message):
		letter_ascii = ord('a')
		for i in range(26):
			await message.add_reaction(emoji[chr(letter_ascii+i)])

	def is_win(self):
		return self.word == self.guessed_word

	def reveal(self, letter):
		temp = ''  # get around with the immutability of string
		for index, character in enumerate(self.word):
			if character == letter:
				temp += character
			else:
				temp += self.guessed_word[index]
		self.guessed_word = temp

	def guess(self, word):
		if not self.verify_guess(word):
			return -1
		# Guess 1 letter
		if len(word) == 1:
			index = self.get_letter_id(word)
			if number_of_matches := self.letter_count[index]:  # Match
				self.letter_count[index] = 0
				self.reveal(word)
				if self.is_win():
					self.status = False
				return number_of_matches
			# No match
			self.guess_cnt += 1
			return 0
		# Guess a whole word
		if word == self.word:
			self.status = False
			return 0
		# Incorrect guess
		self.guess_cnt += 1
		return -2

	def show(self):
		embed = discord.Embed(title='Guess the word to save Hang', color=discord.Color.blurple())
		embed.set_author(name='Hang the man Game', icon_url=self.thumbnail)
		if self.guess_cnt > 1:
			temp = 'es'
		else:
			temp = ''
		embed.set_footer(text='Number of incorrect guess%s: %d/%d' % (temp, self.guess_cnt, self.max_guess))
		embed.add_field(name='========================', value=self.state[self.guess_cnt], inline=False)
		embed.add_field(name='The word has %d letters' % self.word_length, value=self.guessed_word.replace('_', '\\_ '),
						inline=False)
		return embed

	def show_win(self):
		if self.guess_cnt > 1:
			temp = 'es'
		else:
			temp = ''
		embed = discord.Embed(title='%s You won %s' % (emoji['clap'], emoji['clap']),
							  description='You won with %d incorrect guess%s' % (self.guess_cnt, temp),
							  color=discord.Color.green())
		embed.set_author(name='Hang the man Game', icon_url=self.thumbnail)
		embed.add_field(name=self.meaning[0], value=self.meaning[1], inline=False)
		return embed

	def show_lose(self):
		embed = discord.Embed(title='%s You lost %s' % (emoji['tongue'], emoji['tongue']),
							  description='Hang is dead cuz you\'re *retarded* %s\n%s' % (
								  emoji['lol'], self.state[self.guess_cnt]),
							  color=discord.Color.red())
		embed.set_author(name='Hang the man Game', icon_url=self.thumbnail)
		embed.add_field(
			name='The word is **%s**' % self.word,
			value='%s\n%s' % (self.meaning[0], self.meaning[1]),
			inline=False
		)
		return embed


def hm_spam_protection(func):
	async def decorator(self, ctx, *args, **kwargs):
		if self.Client.is_processing:
			return await ctx.send('dmm spam spam cl %s' % emoji['oo'])
		self.Client.is_processing = True
		await func(self, ctx, *args, **kwargs)
		self.Client.is_processing = False

	decorator.__name__ = func.__name__
	decorator.__signature__ = inspect.signature(func)
	return decorator


# Hangman game
class Hangman(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.Client = Hangman_Game()

	@commands.group(help='Hangman game. >hm <word, letter> to guess')
	@hm_spam_protection
	async def hm(self, ctx):
		if ctx.invoked_subcommand is None:
			arg = ctx.message.content.split()
			if len(arg) == 1:
				return await ctx.send('Invalid command')
			arg = arg[1].lower()

			# --------------- >hm guess -----------------------
			if not self.Client.status:
				return await ctx.send('There is no game to play, pls start a game first %s' % emoji['oo'])
			result = self.Client.guess(arg)
			if result == -1:
				return await ctx.send('Invalid guess')
			if not self.Client.status:  # player won the game
				await ctx.send(embed=self.Client.show_win())
				self.Client.__init__()
				return
			# valid guess
			if result == -2:
				await ctx.send('Incorrect guess')
			else:
				if result > 1:
					temp = 'are'
				else:
					temp = 'is'
				await ctx.send(f'There {temp} {result} {arg}')
			if self.Client.guess_cnt > self.Client.max_guess:
				await ctx.send(embed=self.Client.show_lose())
				self.Client.__init__()
				return
			await ctx.send(embed=self.Client.show())


	@hm.command(name='start', help='Start a new game', aliases=['st', 'init', 'initiate', 'on'])
	async def _start(self, ctx):
		if not self.Client.status:
			self.Client.status = True
			return await ctx.send(embed=self.Client.show())
		return await ctx.send('You can only play 1 game at a time %s' % emoji['oo'])


	@hm.command(name='end', help='End the current game', aliases=['abort', 'fs', 'off'])
	async def _end(self, ctx):
		if self.Client.status:
			self.Client.__init__()
			return await ctx.send('The game ended')
		return await ctx.send('There is no game to end -_-')


	@hm.command(name='current', help='Show the current game', aliases=['cr', 'np', 'cs'])
	async def _current(self, ctx):
		if not self.Client.status:
			return await ctx.send('There is no game to play, pls start a game first %s' % emoji['oo'])
		embed = self.Client.show()
		return await ctx.send(embed=embed)


async def setup(bot):
	await bot.add_cog(Hangman(bot))


def _test():
	gen_rand_word()

if __name__ == '__main__':
	_test()
