from dotenv import load_dotenv, find_dotenv
import os

import discord
from discord.ext import tasks, commands

from globalvar.global_var import set_up as data_set_up
data_set_up()

# Load config from env
ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
BETA = os.getenv('BETA')
BETA_TOKEN = os.getenv('DISCORD_BETA_TOKEN')
bot = commands.Bot(command_prefix='>')


@bot.event
async def on_ready():
    #guild = discord.utils.get(bot.guilds, name=GUILD)

    await bot.change_presence(activity=discord.Game(name='>help'))
    print(f'{bot.user} is ready')


# -------------------MAIN-------------------------#
if __name__ == '__main__':
    for filename in os.listdir(os.path.join('.', 'Cogs')):
        if filename.endswith('.py'):
            bot.load_extension('Cogs.%s' % filename[:-3])

    if BETA == '1':
        bot.run(BETA_TOKEN)
    else:
        bot.run(TOKEN)
