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


# Commands related to pictures
class Picture(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	def resize(self, image_name):
		image = Image.open('%s%s' % (image_dir, image_name))
		width = int(float(image.size[0]) * (max_height / float(image.size[1])))
		image = image.resize((width, max_height), Image.ANTIALIAS)
		image.save('%s%s' % (image_dir, image_name))
		image.close()

	@commands.command(name='savepic', help='Save attached image. Syntax: >savepic <name> + <image>')
	async def _savepic(self, ctx, name: str):
		name = name.lower()
		attachment = ctx.message.attachments
		if len(attachment) == 0:
			await ctx.send('Pls attach an image')
			return
		if len(attachment) > 1:
			await ctx.send('Attach 1 image only')
			return
		file = shelve.open(data_dir)
		if name in file['image'].keys():
			await ctx.send('Invalid name')
			return
		extension = attachment[0].url.split('.')[-1]
		all_image = file['image']
		all_image[name] = extension
		file['image'] = all_image
		file.close()
		image_name = '.'.join((name, extension))
		await attachment[0].save('%s%s' % (image_dir, image_name), seek_begin=True, use_cached=False)
		if attachment[0].height > max_height:
			self.resize(image_name)
		await ctx.send('Saved image as %s' % image_name)


	@commands.command(name='delpic', help='Delete a pic saved with >savepic. Syntax: >delpic <name>')
	async def _delpic(self, ctx, name: str):
		name = name.lower()
		file = shelve.open(data_dir)
		all_images = file['image']
		if name not in all_images.keys():
			await ctx.send('Pic not found')
			return
		extension = all_images[name]
		del all_images[name]
		file['image'] = all_images
		file.close()
		image_name = '.'.join((name, extension))
		if os.path.exists('%s%s' % (image_dir, image_name)):
			os.remove('%s%s' % (image_dir, image_name))
		await ctx.send('Removed %s' % image_name)


	@commands.command(name='listpic', help='List all pics. Syntax: >listpic')
	async def _listpic(self, ctx):
		file = shelve.open(data_dir)
		text = '`| '
		for name in file['image'].keys():
			text += name + ' | '
		text += '`'
		file.close()
		await ctx.send(text)

	@commands.command(name='pic', help='Send a pic saved with >savepic. Syntax: >pic <name>')
	async def _pic(self, ctx, name: str):
		name = name.lower()
		file = shelve.open(data_dir)
		if name not in file['image'].keys():
			await ctx.send('Pic not found')
			return
		extension = file['image'][name]
		file.close()
		await ctx.send(content='**%s said**' % ctx.message.author.name,
					   file=discord.File('%s%s.%s' % (image_dir, name, extension)))


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
