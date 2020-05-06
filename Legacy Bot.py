import os
import shelve
from PIL import Image
from random_word import RandomWords
from PyDictionary import PyDictionary
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv('.\\User data.env')
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
bot = commands.Bot(command_prefix='>')
data = shelve.open('.\\data')
data.setdefault('msg_history', [])
data.setdefault('deleted_msg', [])
data.setdefault('image', {})
history = data['msg_history']
deleted_msg = data['deleted_msg']
data.close()
emoji = {'oo': '<:oo:697102602650779778>', 'clap': '👏', 'face_palm': '🤦‍♂', 'tongue': '😛', 'lol': '😄'}
max_height = 400
images_dir = '.\\images\\'
English_dictionary = PyDictionary()
random_word = RandomWords()


def gen_rand_word():
    try:
        word = random_word.get_random_word(hasDictionaryDef="true", minCorpusCount=1000, minLength=4).lower()
        meaning = English_dictionary.meaning(word)
        test = meaning.keys()
        return word, meaning
    except:
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

    def __init__(self):
        self.status = False
        self.is_processing = False
        self.word, meaning = gen_rand_word()
        print(self.word)
        self.guessed_word = '_' * len(self.word)
        self.meaning = [f'**Meaning of \"{self.word}\":**', '']
        for word_type, mean in meaning.items():
            self.meaning[1] += f'**⠂{word_type}:** {mean[0]}\n'
        self.guess_cnt = 0
        self.max_guess = 6
        self.letter_count = [0] * 26
        for letter in self.word:
            self.letter_count[ord(letter) - ord('a')] += 1

    @staticmethod
    def verify_guess(word):
        return word.isalpha()

    def is_win(self):
        return self.word == self.guessed_word

    def reveal(self, letter):
        temp = ''
        for i in range(len(self.word)):
            if self.word[i] == letter:
                temp += letter
            else:
                temp += self.guessed_word[i]
        self.guessed_word = temp

    def guess(self, word):
        if not self.verify_guess(word):
            return -1
        if len(word) == 1:
            if temp := self.letter_count[ord(word) - ord('a')]:
                self.letter_count[ord(word) - ord('a')] = 0
                self.reveal(word)
                if self.is_win():
                    self.status = False
                return temp
            else:
                self.guess_cnt += 1
                return 0
        elif word == self.word:
            self.status = False
            return 0
        else:
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
        embed.add_field(name='The word has %d letters' % len(self.word), value=self.guessed_word.replace('_', '\\_ '),
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


Hangman = Hangman_Game()


def save_msg_history(author, content):
    file = shelve.open('.\\data')
    history.append([author, content])
    file['msg_history'] = history
    file.close()


def save_deleted_msg(author, content):
    file = shelve.open('.\\data')
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
    await bot.change_presence(activity=discord.Game(name='>help'))
    print(f'{bot.user} is ready')


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    #print(message.content)
    save_msg_history(message.author.name, message.content)
    await bot.process_commands(message)


@bot.event
async def on_message_delete(message):
    save_deleted_msg(message.author.name, message.content)
    print(message.author.name, message.content)


@bot.command(name='list', help='Show message history. Syntax: >list <number of msg>')
async def _list(ctx, num_msg: int):
    if num_msg > 30:
        await ctx.send('dmm\nlim 30 ok %s' % emoji['oo'])
        return
    temp = ''
    for author, msg in history[-num_msg - 1:-1]:
        temp += f'**{author}:** {msg}\n'
    await ctx.send(temp)


@bot.command(name='listdel', help='Show deleted message. Syntax: >listdel <number of msg>')
async def _list(ctx, num_msg: int):
    if num_msg > 30:
        await ctx.send('dmm\nlim 30 ok %s' % emoji['oo'])
        return
    temp = ''
    for author, msg in deleted_msg[-num_msg - 1:-1]:
        temp += f'**{author}:** {msg}\n'
    await ctx.send(temp)


@bot.command(name='savepic', help='Save attached image. Syntax: >savepic <name> + <image>')
async def _savepic(ctx, name: str):
    attachment = ctx.message.attachments
    if len(attachment) == 0:
        await ctx.send('Pls attach an image')
        return
    if len(attachment) > 1:
        await ctx.send('Attach 1 image only')
        return
    file = shelve.open('.\\data')
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
    file = shelve.open('.\\data')
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
    file = shelve.open('.\\data')
    if name not in file['image'].keys():
        await ctx.send('Pic not found')
        return
    extension = file['image'][name]
    file.close()
    await ctx.send(content='**%s said**' % ctx.message.author.name,
                   file=discord.File('%s%s.%s' % (images_dir, name, extension)))


@bot.command(name='hm',
             help='Hangman game. Syntax: >hm start (start a game) >hm end (end a game) >hm <word, letter> (guess)')
async def _hm(ctx, arg: str):
    if Hangman.is_processing:
        await ctx.send('dmm spam spam cl %s' % emoji['oo'])
        return
    else: Hangman.is_processing = True
    arg = arg.lower()
    if arg == '':
        await ctx.send('Invalid command')
    elif arg == 'start':
        if not Hangman.status:
            Hangman.status = True
            await ctx.send(embed=Hangman.show())
        else:
            await ctx.send('You can only play 1 game at a time %s' % emoji['oo'])
    elif arg == 'end':
        if Hangman.status:
            Hangman.__init__()
            await ctx.send('The game ended')
        else:
            await ctx.send('There is no game to end -_-')
    elif not Hangman.status:
        await ctx.send('There is no game to play, pls start a game first %s' % emoji['oo'])
    else:
        result = Hangman.guess(arg)
        if result == -1:
            await ctx.send('Invalid guess')
        elif not Hangman.status:  # player won the game
            await ctx.send(embed=Hangman.show_win())
            Hangman.__init__()
        else:  # valid guess
            if result == -2:
                await ctx.send('Incorrect guess')
            else:
                if result == 1:
                    temp = 'is'
                else:
                    temp = 'are'
                await ctx.send(f'There {temp} {result} {arg}')
            if Hangman.guess_cnt > Hangman.max_guess:
                await ctx.send(embed=Hangman.show_lose())
                Hangman.__init__()
            else:
                await ctx.send(embed=Hangman.show())
    Hangman.is_processing = False


# -------------------MAIN-------------------------#
bot.run(TOKEN)
