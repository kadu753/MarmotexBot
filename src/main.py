import discord
from discord.ext import commands
from conf.settings import discordToken

bot = commands.Bot(command_prefix='?')

extensions = ['HorasBot']

@bot.event
async def on_ready():
    print('Bot On')

if __name__ == '__main__':
    for extension in extensions:
        try:
            bot.load_extension(extension)
        except Exception as error:
            print('{} cannot be loaded. [{}]'.format(extension, error))
    bot.run(discordToken)