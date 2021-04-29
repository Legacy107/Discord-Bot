import os
from PIL import Image, ImageDraw, ImageFont
from random import randint
import sys

import discord
from discord.ext import commands

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
from globalvar.global_var import font_dir, emoji


class Ludo_horse:
	ox, oy = 0, 0

	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.ox = x
		self.oy = y
		self.id_on_board = -1
		self.point = 0
		self.finish = False
		self.at_home = True

	def go_home(self):
		self.x = self.ox
		self.y = self.oy
		self.id_on_board = -1
		self.at_home = True

	def go_out(self, coord):
		self.id_on_board = 0
		self.x, self.y = coord[0], coord[1]
		self.at_home = False

	def move(self, coord, sum_dice):
		self.id_on_board += sum_dice
		self.x, self.y = coord[0], coord[1]
		if (point := 62 - self.id_on_board) <= 6:
			self.finish = True
			self.point = 6 - point + 1


class Ludo_player:
	def __init__(self, id, name, color, home):
		self.name = name
		self.horses = []
		self.offset = id * 14
		for x, y in home:
			self.horses.append(Ludo_horse(x, y))
		self.home = home
		self.color = color

	def total_point(self):
		points = 0
		for horse in self.horses:
			points += horse.point
		return points


class Ludo_Game:
	board = [[[230, 17], [230, 53], [230, 89], [230, 125], [230, 161], [230, 197], [230, 233], [194, 233], [158, 233],
			  [122, 233], [86, 233], [50, 233], [14, 233], [14, 269], [14, 305], [50, 305], [86, 305], [122, 305],
			  [158, 305], [194, 305], [230, 305], [230, 341], [230, 377], [230, 413], [230, 449], [230, 485],
			  [230, 521], [266, 521], [302, 521], [302, 485], [302, 449], [302, 413], [302, 377], [302, 341],
			  [302, 305], [338, 305], [374, 305], [410, 305], [446, 305], [482, 305], [518, 305], [518, 269],
			  [518, 233], [482, 233], [446, 233], [410, 233], [374, 233], [338, 233], [302, 233], [302, 197],
			  [302, 161], [302, 125], [302, 89], [302, 53], [302, 17], [266, 17], [266, 53], [266, 89], [266, 125],
			  [266, 161], [266, 197], [266, 233]],
			 [[14, 305], [50, 305], [86, 305], [122, 305], [158, 305], [194, 305], [230, 305], [230, 341], [230, 377],
			  [230, 413], [230, 449], [230, 485], [230, 521], [266, 521], [302, 521], [302, 485], [302, 449],
			  [302, 413], [302, 377], [302, 341], [302, 305], [338, 305], [374, 305], [410, 305], [446, 305],
			  [482, 305], [518, 305], [518, 269], [518, 233], [482, 233], [446, 233], [410, 233], [374, 233],
			  [338, 233], [302, 233], [302, 197], [302, 161], [302, 125], [302, 89], [302, 53], [302, 17], [266, 17],
			  [230, 17], [230, 53], [230, 89], [230, 125], [230, 161], [230, 197], [230, 233], [194, 233], [158, 233],
			  [122, 233], [86, 233], [50, 233], [14, 233], [14, 269], [50, 269], [86, 269], [122, 269], [158, 269],
			  [194, 269], [230, 269]],
			 [[302, 521], [302, 485], [302, 449], [302, 413], [302, 377], [302, 341], [302, 305], [338, 305],
			  [374, 305], [410, 305], [446, 305], [482, 305], [518, 305], [518, 269], [518, 233], [482, 233],
			  [446, 233], [410, 233], [374, 233], [338, 233], [302, 233], [302, 197], [302, 161], [302, 125], [302, 89],
			  [302, 53], [302, 17], [266, 17], [230, 17], [230, 53], [230, 89], [230, 125], [230, 161], [230, 197],
			  [230, 233], [194, 233], [158, 233], [122, 233], [86, 233], [50, 233], [14, 233], [14, 269], [14, 305],
			  [50, 305], [86, 305], [122, 305], [158, 305], [194, 305], [230, 305], [230, 341], [230, 377], [230, 413],
			  [230, 449], [230, 485], [230, 521], [266, 521], [266, 485], [266, 449], [266, 413], [266, 377],
			  [266, 341], [266, 305]],
			 [[518, 233], [482, 233], [446, 233], [410, 233], [374, 233], [338, 233], [302, 233], [302, 197],
			  [302, 161], [302, 125], [302, 89], [302, 53], [302, 17], [266, 17], [230, 17], [230, 53], [230, 89],
			  [230, 125], [230, 161], [230, 197], [230, 233], [194, 233], [158, 233], [122, 233], [86, 233], [50, 233],
			  [14, 233], [14, 269], [14, 305], [50, 305], [86, 305], [122, 305], [158, 305], [194, 305], [230, 305],
			  [230, 341], [230, 377], [230, 413], [230, 449], [230, 485], [230, 521], [266, 521], [302, 521],
			  [302, 485], [302, 449], [302, 413], [302, 377], [302, 341], [302, 305], [338, 305], [374, 305],
			  [410, 305], [446, 305], [482, 305], [518, 305], [518, 269], [482, 269], [446, 269], [410, 269],
			  [374, 269], [338, 269], [302, 269]]]
	home = [[[15, 17], [51, 17], [15, 53], [51, 53]],
			[[15, 482], [51, 482], [15, 518], [51, 518]],
			[[481, 482], [517, 482], [481, 518], [517, 518]],
			[[481, 17], [517, 17], [481, 53], [517, 53]]]
	color = ['red', 'green', 'yellow', 'blue']
	font = ImageFont.truetype(font_dir, 22)
	thumbnail = 'https://cdn.discordapp.com/attachments/706438294245736469/715542480581558392/images.png'
	winning_image = 'https://cdn.discordapp.com/attachments/706438294245736469/716574811320746064/45e.jpg'
	log_go_out = '{player}\'s horse{id} entered the race'
	log_move_ahead = '{player}\'s horse{id} moved {steps} step forward'
	log_kick = ' and kicked {kicked_player}\'s horse'
	invalid_msg = 'Invalid move'
	main_image = os.path.join(parentdir, 'ludo', 'self.Client.jpg')
	temp_image = os.path.join(parentdir, 'ludo', 'ludo_tmp.jpg')

	def __init__(self, players):
		self.status = False
		self.is_processing = False
		self.turn = 0
		self.dice = []
		self.rolled = False
		self.log = ''
		self.players = []
		for id, player in enumerate(players):
			self.players.append(Ludo_player(id, player, self.color[id], self.home[id]))

	def prepare_image(self):
		off_set = 5
		file = Image.open(self.main_image)
		draw = ImageDraw.Draw(file)
		for player in self.players:
			for id, horse in enumerate(player.horses):
				draw.ellipse((horse.x + off_set, horse.y + off_set, horse.x + 36 - off_set, horse.y + 36 - off_set),
							 fill=player.color, outline='gray', width=2)
				draw.text((horse.x + 13, horse.y + 1), text=str(id + 1), fill='white', font=self.font)
		file.save(self.temp_image)
		file.close()

	def show(self):
		self.prepare_image()
		embed = discord.Embed(title=self.log, color=discord.Color.blurple())
		embed.description = 'It\'s **%s\'s** turn. Pls `>ld roll` the dice' % self.players[self.turn].name
		embed.set_author(name='Ludo Game', icon_url=self.thumbnail)
		file = discord.File(self.temp_image, filename="ludo_tmp.jpg")
		embed.set_image(url="attachment://ludo_tmp.jpg")
		return file, embed

	def show_win(self):
		embed = discord.Embed(
			title='**%s %s won the game %s' % (emoji['clap'], self.players[self.turn].name, emoji['clap']),
			color=discord.Color.green())
		embed.set_author(name='Ludo Game', icon_url=self.thumbnail)
		embed.set_image(url=self.winning_image)
		return embed

	def check_win(self):
		player = self.players[self.turn]
		sum_point = 0
		for horse in player.horses:
			sum_point += horse.point
		if sum_point == 18:
			self.status = False
			return True
		return False

	def verify(self, name):
		if self.is_processing:
			return 'dmm spam spam cl %s' % emoji['oo']
		if not self.status:
			return 'Please start a game first'
		if name != self.players[self.turn].name:
			return 'It\'s not your turn bruh'
		return ''

	def is_special_dice(self):
		return self.dice[0] == self.dice[1] or (sum(self.dice) == 7 and min(self.dice) == 1)

	def next_turn(self):
		self.turn = (self.turn + 1) % len(self.players)

	def horse_at(self, id, kick=False):
		for player in self.players:
			for horse in player.horses:
				if horse.id_on_board != -1 and (horse.id_on_board + player.offset) % len(self.board[0]) == id:
					if kick:
						horse.go_home()
					return player.name
		return ''

	def make_log(self, log, player, horse_id, steps=0, kicked_player=''):
		self.log = log.format(player=player, id=horse_id, steps=steps)
		if kicked_player:
			self.log += self.log_kick.format(kicked_player=kicked_player)

	# Make a move and test for move if test==True
	def move(self, id, test=False):
		current_player = self.players[self.turn]
		horse = current_player.horses[id - 1]
		sum_dice = sum(self.dice)
		kick = not test
		if horse.at_home:
			if not self.is_special_dice():
				return self.invalid_msg
			player_in_way = self.horse_at(current_player.offset, kick=kick)
			if player_in_way == current_player.name:
				return self.invalid_msg
			if not test:
				horse.go_out(self.board[self.turn][0])
				self.make_log(log=self.log_go_out, player=current_player.name, horse_id=id, kicked_player=player_in_way)
		elif horse.finish:
			if not (self.dice[0] == self.dice[1] and self.dice[0] == horse.point):
				return self.invalid_msg
			for other_horse in current_player.horses:
				if other_horse.id_on_board == horse.id_on_board + 1:
					return self.invalid_msg
			if not test:
				horse.move(self.board[self.turn][horse.id_on_board + 1], 1)
				self.make_log(log=self.log_move_ahead, player=current_player.name, horse_id=id, steps=1)
		else:
			for i in range(1, sum_dice):
				player_in_way = self.horse_at((horse.id_on_board + i + current_player.offset) % len(self.board[0]))
				if player_in_way:
					return self.invalid_msg
			player_in_way = self.horse_at((horse.id_on_board + sum_dice + current_player.offset) % len(self.board[0]),
										  kick=kick)
			if player_in_way == current_player.name:
				return self.invalid_msg
			if not test:
				horse.move(self.board[self.turn][horse.id_on_board + sum_dice], sum_dice)
				self.make_log(log=self.log_move_ahead, player=current_player.name, horse_id=id, steps=sum_dice,
							  kicked_player=player_in_way)
		if not test and not self.is_special_dice():
			self.next_turn()
		return ''

	def has_valid_move(self):
		has_valid_move = False
		for id in range(1, len(self.players[self.turn].horses) + 1):
			has_valid_move |= not bool(self.move(id, test=True))
		return has_valid_move


# Ludo game
class Ludo(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.Client = Ludo_Game(['Legacy'])

	@commands.group(help='Ludo game')
	async def ld(self, ctx):
		if ctx.invoked_subcommand is None:
			await ctx.send('Invalid command')


	@ld.command(name='start', help='Start a new game')
	async def _start(self, ctx):
		if self.Client.is_processing:
			return await ctx.send('dmm spam spam cl %s' % emoji['oo'])
		self.Client.is_processing = True
		if not self.self.Client.status:
			mention = ctx.message.mentions
			users = []
			for user in mention:
				users.append(user.name)
			self.Client.__init__(users)
			self.Client.status = True
			file, embed = self.Client.show()
			await ctx.send(file=file, embed=embed)
		else:
			await ctx.send('You can only play 1 game at a time %s' % emoji['oo'])
		self.Client.is_processing = False


	@ld.command(name='end', help='End current game')
	async def _end(self, ctx):
		if self.Client.is_processing:
			return await ctx.send('dmm spam spam cl %s' % emoji['oo'])
		self.Client.is_processing = True
		if self.Client.status:
			self.Client.status = False
			await ctx.send('The game ended')
		else:
			await ctx.send('There is no game to end -_-')
		self.Client.is_processing = False


	@ld.command(name='current', hlep='Show current game')
	async def _current(self, ctx):
		if self.Client.is_processing:
			return await ctx.send('dmm spam spam cl %s' % emoji['oo'])
		self.Client.is_processing = True
		file, embed = self.Client.show()
		await ctx.send(file=file, embed=embed)
		self.Client.is_processing = False


	@ld.command(name='roll', help='roll dice')
	async def _roll(self, ctx):
		if msg := self.Client.verify(ctx.message.author.name):
			return await ctx.send(msg)
		if self.Client.rolled:
			return await ctx.send('You\'ve already rolled')
		self.Client.is_processing = True
		self.Client.rolled = True
		dice = [randint(1, 6), randint(1, 6)]
		self.Client.dice = dice
		await ctx.send('**%s** rolls the dice %s %s' % (
			ctx.message.author.name,
			emoji['dice%s' % dice[0]],
			emoji['dice%s' % dice[1]]
		))
		if not self.Client.has_valid_move():
			self.Client.next_turn()
			self.Client.rolled = False
			await ctx.send('Skipped %s\'s turn' % ctx.message.author.name)
			file, embed = self.Client.show()
			await ctx.send(file=file, embed=embed)
		self.Client.is_processing = False


	async def ld_move(self, ctx, id):
		if msg := self.Client.verify(ctx.message.author.name):
			return await ctx.send(msg)
		if not self.Client.rolled:
			return await ctx.send('You haven\'t rolled the dice yet duh!')
		self.Client.is_processing = True
		if msg := self.Client.move(id):
			self.Client.is_processing = False
			return await ctx.send(msg)
		self.Client.rolled = False
		if self.Client.check_win():
			return await ctx.send(embed=self.Client.show_win())
		file, embed = self.Client.show()
		await ctx.send(file=file, embed=embed)
		self.Client.is_processing = False


	@ld.command(name='1', help='Move 1')
	async def _1(self, ctx):
		await self.ld_move(ctx, 1)


	@ld.command(name='2', help='Move 2')
	async def _2(self, ctx):
		await self.ld_move(ctx, 2)


	@ld.command(name='3', help='Move 3')
	async def _3(self, ctx):
		await self.ld_move(ctx, 3)


	@ld.command(name='4', help='Move 4')
	async def _4(self, ctx):
		await self.ld_move(ctx, 4)


	@ld.command(name='skip', help='Skip a move')
	@commands.is_owner()
	async def _skip(self, ctx):
		if msg := self.Client.verify(ctx.message.author.name):
			return await ctx.send(msg)
		self.Client.next_turn()
		self.Client.rolled = False
		await ctx.send('Skipped %s\'s turn' % ctx.message.author.name)
		file, embed = self.Client.show()
		await ctx.send(file=file, embed=embed)


def setup(bot):
	bot.add_cog(Ludo(bot))
