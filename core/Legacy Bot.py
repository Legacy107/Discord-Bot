import os
import unicodedata
import shelve
from random import randint
import sys

import discord
from discord.ext import tasks, commands
from dotenv import load_dotenv, find_dotenv

sys.path.insert(0, '..' + os.path.sep)
from globalvar import global_var
global_var.set_up()

# Load config from env
ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)
TOKEN = os.getenv('DISCORD_TOKEN')
ADMIN_ID = os.getenv('ADMIN_ID')
GUILD = os.getenv('DISCORD_GUILD')
BETA = os.getenv('BETA')
BETA_TOKEN = os.getenv('DISCORD_BETA_TOKEN')
bot = commands.Bot(command_prefix='>')


async def is_admin(ctx):
    return ctx.author.id == ADMIN_ID


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


@bot.command(name='test', help='Test')
@commands.is_owner()
async def _test(ctx, num1: int, num2: int, horse_id: int):
    Ludo.dice = [num1, num2]
    Ludo.move(horse_id)
    if Ludo.check_win():
        await ctx.send(embed=Ludo.show_win())
    else:
        file, embed = Ludo.show()
        await ctx.send(file=file, embed=embed)


# -------------------MAIN-------------------------#
if __name__ == '__main__':
    for filename in os.listdir(os.path.join('..', 'Cogs')):
        if filename.endswith('.py'):
            bot.load_extension('Cogs.%s' % filename[:-3])

    if BETA == '1':
        bot.run(BETA_TOKEN)
    else:
        bot.run(TOKEN)