import os
import unicodedata
import shelve
import re
import textwrap
from random import randint

import discord
from PIL import Image, ImageDraw, ImageFont
from PyDictionary import PyDictionary
from discord.ext import tasks, commands
from dotenv import load_dotenv, find_dotenv
from random_word import RandomWords

# Get token
ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
bot = commands.Bot(command_prefix='>')

# Dir
images_dir = os.path.join('.','images','')
audio_dir = os.path.join('.','audio','')
ffmpeg_dir = os.path.join('C:','Program Files (x86)','ffmpeg','bin','ffmpeg.exe')
font_dir = os.path.join('.','font','VNF-Comic Sans.ttf')
data_dir = os.path.join('.','data')

data = shelve.open(data_dir)
data.setdefault('msg_history', [])
data.setdefault('deleted_msg', [])
data.setdefault('image', {})
history = data['msg_history']
deleted_msg = data['deleted_msg']
data.close()
emoji = {'oo': '<:oo:697102602650779778>', 'clap': '👏', 'face_palm': '🤦‍♂', 'tongue': '😛', 'lol': '😄',
         'dice1': '<:dice1:714008777942237215>',
         'dice2': '<:dice2:714008777644572754>', 'dice3': '<:dice3:714008777849831427>',
         'dice4': '<:dice4:714008778701537430>', 'dice5': '<:dice5:714008778806394922>',
         'dice6': '<:dice6:714008778764320788>', 'a': '🇦', 'b': '🇧', 'c': '🇨', 'd': '🇩', 'e': '🇪', 'f': '🇫',
         'g': '🇬', 'h': '🇭', 'i': '🇮', 'j': '🇯', 'k': '🇰', 'l': '🇱', 'm': '🇲', 'n': '🇳', 'o': '🇴', 'p': '🇵',
         'q': '🇶', 'r': '🇷', 's': '🇸', 't': '🇹', 'u': '🇺', 'v': '🇻', 'w': '🇼', 'x': '🇽', 'y': '🇾', 'z': '🇿'}
max_height = 400
max_msg = 128
English_dictionary = PyDictionary()
random_word = RandomWords()
RE_has_digit = re.compile('\d|\'')


async def is_Legacy(ctx):
    return ctx.author.id == 661137333474557972


def gen_rand_word():
    try:
        word = random_word.get_random_word(hasDictionaryDef="true", minCorpusCount=1000, minLength=4).lower()
        if RE_has_digit.search(word):
            print('Word contains digit')
            return gen_rand_word()
        meaning = English_dictionary.meaning(word)
        test = meaning.keys()
        return word, meaning
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
            self.meaning[1] += f'**⠂{word_type}:** {mean[0]}\n'

        self.guess_cnt = 0
        self.max_guess = 6
        self.letter_count = [0] * 26
        for letter in self.word:
            if (index := self.get_letter_id(letter)) < 26 and index >= 0:
                self.letter_count[index] += 1

    @staticmethod
    def verify_guess(word):
        return word.isalpha()

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
        # Incorect guess
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
        embed.add_field(name='The word is **%s**' % self.word, value='%s\n%s' % (self.meaning[0], self.meaning[1]),
                        inline=False)
        return embed


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
        sum = 0
        for horse in self.horses:
            sum += horse.point
        return sum


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
    main_image = os.path.join('.','ludo','ludo.jpg')
    temp_image = os.path.join('.','ludo','ludo_tmp.jpg')

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
        elif not self.status:
            return 'Please start a game first'
        elif name != self.players[self.turn].name:
            return 'It\'s not your turn bruh'
        else:
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


def save_msg_history(author, content):
    file = shelve.open(data_dir)
    if len(history) > max_msg:
        del history[0]
    history.append([author, content])
    file['msg_history'] = history
    file.close()


def save_deleted_msg(author, content):
    file = shelve.open(data_dir)
    if len(deleted_msg) > max_msg:
        del deleted_msg[0]
    deleted_msg.append([author, content])
    file['deleted_msg'] = deleted_msg
    file.close()

    
def resize(image_name):
    image = Image.open('%s%s' % (images_dir, image_name))
    width = int(float(image.size[0]) * (max_height / float(image.size[1])))
    image = image.resize((width, max_height), Image.ANTIALIAS)
    image.save('%s%s' % (images_dir, image_name))
    image.close()


@bot.event
async def on_ready():
    guild = discord.utils.get(bot.guilds, name=GUILD)

    async def get_unicode_char():
        cnt = 97
        dic = {}
        for i in range(26):
            dic[chr(cnt)] = unicodedata.lookup('REGIONAL INDICATOR SYMBOL LETTER %s' % chr(cnt).upper())
            cnt += 1
        print(dic)

    await bot.change_presence(activity=discord.Game(name='>help'))
    print(f'{bot.user} is ready')


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    # print(message.content)
    save_msg_history(message.author.name, message.content)
    await bot.process_commands(message)


@bot.event
async def on_message_delete(message):
    if message.author == bot.user:
        return
    save_deleted_msg(message.author.name, message.content)
    print(message.author.name, message.content)


@bot.command(name='wipe', help='Wipe all message data')
@commands.check(is_Legacy)
async def _wipe_msg_data(ctx):
    history.clear()
    deleted_msg.clear()
    file = shelve.open(data_dir, flag='r')
    image_data = file['image']
    file.close()
    os.remove(os.path.join('.','data.dat'))
    os.remove(os.path.join('.','data.bak'))
    os.remove(os.path.join('.','data.dir'))
    file = shelve.open(data_dir, flag='n')
    file.setdefault('image', image_data)
    file.close()
    await ctx.send('Successfully wiped out msg data')


@bot.command(name='list', help='Show message history. Syntax: >list <number of msg>')
async def _list(ctx, num_msg: int):
    if num_msg > 30:
        await ctx.send('dmm\nlim 30 ok %s' % emoji['oo'])
        return
    temp = ''
    for author, msg in history[-num_msg - 1:-1]:  # -1: exclude >list
        temp += f'**{author}:** {msg}\n'
    await ctx.send(temp)


@bot.command(name='listdel', help='Show deleted message. Syntax: >listdel <number of msg>')
async def _list(ctx, num_msg: int):
    if num_msg > 30:
        await ctx.send('dmm\nlim 30 ok %s' % emoji['oo'])
        return
    temp = ''
    for author, msg in deleted_msg[-num_msg:]:
        temp += f'**{author}:** {msg}\n'
    await ctx.send(temp)


@bot.command(name='savepic', help='Save attached image. Syntax: >savepic <name> + <image>')
async def _savepic(ctx, name: str):
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
    await attachment[0].save('%s%s' % (images_dir, image_name), seek_begin=True, use_cached=False)
    if attachment[0].height > max_height:
        resize(image_name)
    await ctx.send('Saved image as %s' % image_name)


@bot.command(name='delpic', help='Delete a pic saved with >savepic. Syntax: >delpic <name>')
async def _delpic(ctx, name: str):
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
    if os.path.exists('%s%s' % (images_dir, image_name)):
        os.remove('%s%s' % (images_dir, image_name))
    await ctx.send('Removed %s' % image_name)


@bot.command(name='pic', help='Send a pic saved with >savepic. Syntax: >pic <name>')
async def _pic(ctx, name: str):
    name = name.lower()
    file = shelve.open(data_dir)
    if name not in file['image'].keys():
        await ctx.send('Pic not found')
        return
    extension = file['image'][name]
    file.close()
    await ctx.send(content='**%s said**' % ctx.message.author.name,
                   file=discord.File('%s%s.%s' % (images_dir, name, extension)))


@bot.command(name='hhh', help=u'Huấn Rô Sì')
async def _hhh(ctx, *, arg):
    image_name = 'hhh.png'
    font = ImageFont.truetype(font_dir, 18)
    header = u'Này {users}! Anh Huấn tặng chú 1 câu'
    users = ctx.message.mentions
    names = [user.name for user in users]
    text = ' '.join(arg.split()[len(users):]) + u' em nhé!'  # remove mentions
    max_letters = 23
    color = 'black'

    image = Image.open('%s%s' % (images_dir, image_name))
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

    image.save('%stmp%s' % (images_dir, image_name))
    await ctx.send(file=discord.File('%stmp%s' % (images_dir, image_name)))


@bot.command(name='hm',
             help='Hangman game. Syntax: >hm start (start a game) >hm end (end a game) >hm <word, letter> (guess)')
async def _hm(ctx, arg: str):
    arg = arg.lower()
    if Hangman.is_processing:
        return await ctx.send('dmm spam spam cl %s' % emoji['oo'])
    Hangman.is_processing = True
    try:
        arg = arg.lower()
        if arg == '':
            return await ctx.send('Invalid command')

        # --------------- >hm start -----------------------
        if arg == 'start':
            if not Hangman.status:
                Hangman.status = True
                return await ctx.send(embed=Hangman.show())
            return await ctx.send('You can only play 1 game at a time %s' % emoji['oo'])

        # --------------- >hm end -------------------------
        if arg == 'end':
            if Hangman.status:
                Hangman.__init__()
                return await ctx.send('The game ended')
            return await ctx.send('There is no game to end -_-')
        if not Hangman.status:
            return await ctx.send('There is no game to play, pls start a game first %s' % emoji['oo'])

        # --------------- >hm current ---------------------
        if arg == 'current':
            embed = Hangman.show()
            return await ctx.send(embed=embed)

        # --------------- >hm guess -----------------------
        result = Hangman.guess(arg)
        if result == -1:
            return await ctx.send('Invalid guess')
        if not Hangman.status:  # player won the game
            await ctx.send(embed=Hangman.show_win())
            Hangman.__init__()
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
        if Hangman.guess_cnt > Hangman.max_guess:
            await ctx.send(embed=Hangman.show_lose())
            Hangman.__init__()
            return
        await ctx.send(embed=Hangman.show())
    finally:
        Hangman.is_processing = False


@bot.group(help='Ludo game')
async def ld(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send('Invalid command')


@ld.command(name='start', help='Start a new game')
async def _start(ctx):
    if Ludo.is_processing:
        return await ctx.send('dmm spam spam cl %s' % emoji['oo'])
    Ludo.is_processing = True
    if not Ludo.status:
        mention = ctx.message.mentions
        users = []
        for user in mention:
            users.append(user.name)
        Ludo.__init__(users)
        Ludo.status = True
        file, embed = Ludo.show()
        await ctx.send(file=file, embed=embed)
    else:
        await ctx.send('You can only play 1 game at a time %s' % emoji['oo'])
    Ludo.is_processing = False


@ld.command(name='end', help='End current game')
async def _end(ctx):
    if Ludo.is_processing:
        return await ctx.send('dmm spam spam cl %s' % emoji['oo'])
    Ludo.is_processing = True
    if Ludo.status:
        Ludo.status = False
        await ctx.send('The game ended')
    else:
        await ctx.send('There is no game to end -_-')
    Ludo.is_processing = False


@ld.command(name='current', hlep='Show current game')
async def _current(ctx):
    if Ludo.is_processing:
        return await ctx.send('dmm spam spam cl %s' % emoji['oo'])
    Ludo.is_processing = True
    file, embed = Ludo.show()
    await ctx.send(file=file, embed=embed)
    Ludo.is_processing = False


@ld.command(name='roll', help='roll dice')
async def _roll(ctx):
    if msg := Ludo.verify(ctx.message.author.name):
        return await ctx.send(msg)
    if Ludo.rolled:
        return await ctx.send('You\'ve already rolled')
    Ludo.is_processing = True
    Ludo.rolled = True
    dice = [randint(1, 6), randint(1, 6)]
    Ludo.dice = dice
    await ctx.send('**%s** rolls the dice %s %s' % (ctx.message.author.name,
                                                    emoji['dice%s' % dice[0]], emoji['dice%s' % dice[1]]))
    if not Ludo.has_valid_move():
        Ludo.next_turn()
        Ludo.rolled = False
        await ctx.send('Skipped %s\'s turn' % ctx.message.author.name)
        file, embed = Ludo.show()
        await ctx.send(file=file, embed=embed)
    Ludo.is_processing = False


async def ld_move(ctx, id):
    if msg := Ludo.verify(ctx.message.author.name):
        return await ctx.send(msg)
    if not Ludo.rolled:
        return await ctx.send('You haven\'t rolled the dice yet duh!')
    Ludo.is_processing = True
    if msg := Ludo.move(id):
        Ludo.is_processing = False
        return await ctx.send(msg)
    Ludo.rolled = False
    if Ludo.check_win():
        return await ctx.send(embed=Ludo.show_win())
    file, embed = Ludo.show()
    await ctx.send(file=file, embed=embed)
    Ludo.is_processing = False


@ld.command(name='1', help='Move 1')
async def _1(ctx):
    await ld_move(ctx, 1)


@ld.command(name='2', help='Move 2')
async def _2(ctx):
    await ld_move(ctx, 2)


@ld.command(name='3', help='Move 3')
async def _3(ctx):
    await ld_move(ctx, 3)


@ld.command(name='4', help='Move 4')
async def _4(ctx):
    await ld_move(ctx, 4)


@ld.command(name='skip', help='Skip a move')
@commands.check(is_Legacy)
async def _skip(ctx):
    if msg := Ludo.verify(ctx.message.author.name):
        return await ctx.send(msg)
    Ludo.next_turn()
    Ludo.rolled = False
    await ctx.send('Skipped %s\'s turn' % ctx.message.author.name)
    file, embed = Ludo.show()
    await ctx.send(file=file, embed=embed)


@bot.command(name='join', help='Join a voice channel')
async def _join(ctx):
    if ctx.message.author.voice:
        channel = ctx.message.author.voice.channel
        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)
        await channel.connect()
    else:
        await ctx.send('You must connect to a voice channel first')


@bot.command(name='leave', help='Leave a voice channel')
async def _leave(ctx):
    if ctx.message.author.voice:
        if not (guild := ctx.voice_client):
            await ctx.send('The bot hasn\'t connected to a voice channel')
        else:
            await guild.disconnect()
    else:
        await ctx.send('You must connect to a voice channel first')


@bot.command(name='play', help='Play an audio file')
async def _play(ctx, name: str):
    if not ctx.voice_client:
        return await ctx.send('The bot hasn\'t connected to a voice channel')
    name += '.mp3'
    audio_file = '%s%s' % (audio_dir, name)
    if os.path.exists(audio_file):
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(executable=ffmpeg_dir, source=audio_file))
        ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)
        await ctx.send('Playing %s' % name)
    else:
        await ctx.send('File not found')


@bot.command(name='volume', help='Adjust bot\'s volume (0 - 100)')
async def _volume(ctx, volume: int):
    if ctx.voice_client is None:
        return await ctx.send('The bot hasn\'t connected to a voice channel')
    ctx.voice_client.source.volume = volume / 100
    await ctx.send("Changed volume to %d" % volume)


@bot.command(name='stop', help='Stop playing audio')
async def _stop(ctx):
    ctx.voice_client.stop()


@bot.command(name='pause', help='Pause audio')
async def _pause(ctx):
    ctx.voice_client.pause()


@bot.command(name='resume', help='Resume audio')
async def _resume(ctx):
    ctx.voice_client.resume()


@bot.command(name='test', help='Test')
@commands.check(is_Legacy)
async def _test(ctx, num1: int, num2: int, horse_id: int):
    Ludo.dice = [num1, num2]
    Ludo.move(horse_id)
    if Ludo.check_win():
        await ctx.send(embed=Ludo.show_win())
    else:
        file, embed = Ludo.show()
        await ctx.send(file=file, embed=embed)


# -------------------MAIN-------------------------#
Hangman = Hangman_Game()
# Ludo = Ludo_Game(['Legacy'])
bot.run(TOKEN)
