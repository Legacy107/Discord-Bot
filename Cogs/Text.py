import os
import shelve
import sys

import discord
from discord.ext import commands

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
from globalvar.global_var import data_dir, emoji, max_msg
from utils import api


# Commands related to text
class Text(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

		data = shelve.open(data_dir)
		self.history = data['msg_history']
		self.deleted_msg = data['deleted_msg']
		data.close()

		self.facts = []

	@commands.command(name='wipe', help='Wipe all message data')
	@commands.is_owner()
	async def _wipe_msg_data(self, ctx):
		os.remove(data_dir + '.dat')
		os.remove(data_dir + '.bak')
		os.remove(data_dir + '.dir')
		file = shelve.open(data_dir, flag='n')
		file.close()
		await ctx.send('Successfully wiped out message data')

	def save_msg_history(self, author, content):
		file = shelve.open(data_dir)
		if len(self.history) > max_msg:
			del self.history[0]
		self.history.append([author, content])
		file['msg_history'] = self.history
		file.close()

	def save_deleted_msg(self, author, content):
		file = shelve.open(data_dir)
		if len(self.deleted_msg) > max_msg:
			del self.deleted_msg[0]
		self.deleted_msg.append([author, content])
		file['deleted_msg'] = self.deleted_msg
		file.close()

	@commands.Cog.listener()
	async def on_message(self, message):
		if message.author == self.bot.user:
			return

		self.save_msg_history(message.author.name, message.content)

	@commands.Cog.listener()
	async def on_message_delete(self, message):
		if message.author == self.bot.user:
			return
		self.save_deleted_msg(message.author.name, message.content)
		print(message.author.name, message.content)

	@commands.command(name='list', help='Show message history. Syntax: >list <number of msg>')
	async def _list(self, ctx, num_msg: int):
		if num_msg > 30:
			await ctx.send(f'dmm\nlim 30 ok {emoji["oo"]}')
			return
		temp = ''
		for author, msg in self.history[-num_msg - 1:-1]:  # -1: exclude >list
			temp += f'**{author}:** {msg}\n'
		await ctx.send(temp)

	@commands.command(name='listdel', help='Show deleted message. Syntax: >listdel <number of msg>')
	async def _listdel(self, ctx, num_msg: int):
		if num_msg > 30:
			await ctx.send(f'dmm\nlim 30 ok {emoji["oo"]}')
			return
		temp = ''
		for author, msg in self.deleted_msg[-num_msg:]:
			temp += f'**{author}:** {msg}\n'
		await ctx.send(temp)

	@commands.command(name='fact', help='Get amazing facts')
	async def _fact(self, ctx):
		if not self.facts:
			self.facts = await api.get_amazing_fact()

		fact = self.facts.pop()
		exploding_head = emoji[':O']

		embed = discord.Embed(
			title=f'{exploding_head} AMAZING FACT!!! {exploding_head}',
			description=f'=================================\n**{fact["content"]}**',
			url=fact['url'],
			color=discord.Color.dark_blue()
		)
		embed.set_thumbnail(url=fact['image_url'])
		embed.set_footer(text=f'Fact: mentalfloss.com\tImage: {fact["image_credit"]}')
		await ctx.send(embed=embed)


async def setup(bot):
	await bot.add_cog(Text(bot))
