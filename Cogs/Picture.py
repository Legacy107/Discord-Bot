import aiohttp
import io
import os
from PIL import Image, ImageDraw, ImageFont
import shelve
import sys

import discord
from discord.ext import commands
import textwrap

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
from globalvar.global_var import image_dir, data_dir, font_dir, max_height
from utils.database import PicDatabase


# Commands related to pictures
class Picture(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.db_client = PicDatabase()
		self.archive_channel = None

	@staticmethod
	def resize(image_name):
		image = Image.open('%s%s' % (image_dir, image_name))
		width = int(float(image.size[0]) * (max_height / float(image.size[1])))
		image = image.resize((width, max_height), Image.ANTIALIAS)
		image.save('%s%s' % (image_dir, image_name))
		image.close()

	@commands.command(name='savepic', help='Save attached image. Syntax: >savepic <name> + <image>')
	async def _savepic(self, ctx, name: str, *, full_name=''):
		name = name.lower()
		# set default value equal to name
		full_name = full_name or name
		attachment = ctx.message.attachments
		if len(attachment) == 0:
			return await ctx.send('Pls attach an image')
		if len(attachment) > 1:
			return await ctx.send('Attach 1 image only')
		if await self.db_client.has_pic(name):
			return await ctx.send('Invalid name')

		extension = attachment[0].url.split('.')[-1]
		image_name = '.'.join((name, extension))

		await attachment[0].save('%s%s' % (image_dir, image_name), seek_begin=True, use_cached=False)
		if attachment[0].height > max_height:
			self.resize(image_name)
		res = await self.archive_channel.send(file=discord.File('%s%s' % (image_dir, image_name)))
		pic_url = res.attachments[0].url

		await self.db_client.add_pic(name, pic_url, full_name)

		await ctx.send('Successfully saved image as %s' % image_name)


	@commands.command(name='delpic', help='Delete a pic saved with >savepic. Syntax: >delpic <name>')
	async def _delpic(self, ctx, name: str):
		name = name.lower()
		if not await self.db_client.has_pic(name):
			return await ctx.send('Pic not found')

		await self.db_client.delete_pic(name)

		await ctx.send('Successfully removed pic %s' % name)


	@commands.command(name='listpic', help='List all pics. Syntax: >listpic')
	async def _listpic(self, ctx):
		text = '`| '
		all_pics = await self.db_client.get_all_pics()
		for pic in all_pics:
			text += pic['id'] + ' ' + ('(' + pic['name'] + ')' if pic['id'] != pic['name'] else '') + ' | '
			# avoid exceeding msg length limit
			if len(text) > 1500:
				text += '`'
				await ctx.send(text)
				text = text = '`| '
		text += '`'
		# not empty
		if len(text) > 4:
			await ctx.send(text)

	@commands.command(name='pic', help='Send a pic saved with >savepic. Syntax: >pic <name>')
	async def _pic(self, ctx, name: str):
		name = name.lower()
		if not await self.db_client.has_pic(name):
			return await ctx.send('Pic not found')

		pic_url = await self.db_client.get_pic_url(name)
		file_name = pic_url.split('/')[-1]
		async with aiohttp.ClientSession() as session:
			async with session.get(pic_url) as res:
				if res.status != 200:
					return await ctx.send('Network error. Pls try again.')
				data = io.BytesIO(await res.read())
				await ctx.send(content='**%s said**' % ctx.message.author.name, file=discord.File(data, file_name))


	@commands.command(name='hhh', help=u'Huấn Rô Sì')
	async def _hhh(self, ctx, *, arg):
		image_name = 'hhh.png'
		font = ImageFont.truetype(font_dir, 18)
		header = u'Này {users}! Anh Huấn tặng chú 1 câu'
		users = ctx.message.mentions
		names = [user.name for user in users]
		text = ' '.join(arg.split()[len(users):]) + u' em nhé!'  # remove mentions
		max_letters = 23
		color = 'black'

		image = Image.open('%s%s' % (image_dir, image_name))
		image_width, image_height = image.size
		draw = ImageDraw.Draw(image)

		header = header.format(users=', '.join(names))
		para = textwrap.wrap(header, width=max_letters)
		current_height = 0
		for line in para:
			width, height = draw.textsize(line, font=font)
			draw.text(((image_width - width) / 2, current_height), line, font=font, fill=color)
			current_height += height

		para = textwrap.wrap(text, width=max_letters)[::-1]  # print in reverse order
		print(para)
		current_height = image_height - 25
		for line in para:
			width, height = draw.textsize(line, font=font)
			draw.text(((image_width - width) / 2, current_height), line, font=font, fill=color)
			current_height -= height

		image.save('%stmp%s' % (image_dir, image_name))
		await ctx.send(file=discord.File('%stmp%s' % (image_dir, image_name)))

def setup(bot):
	bot.add_cog(Picture(bot))
