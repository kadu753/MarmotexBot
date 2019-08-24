import discord
from discord.ext import commands
import asyncio
import psycopg2
import operator
import databaseconnection
from datetime import datetime, timedelta
from pytz import timezone


class HorasBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conexao = databaseconnection.DatabaseConnection()
        self.fila_tempo = {}
        self.fuso_horario = timezone('America/Sao_Paulo')

    @asyncio.coroutine
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if after.channel is not None:
            if await self.conexao.queryRegistro("SELECT EXISTS(SELECT 1 FROM usuario WHERE id={})".format(member.id)):
                self.fila_tempo[member.id] = await self.conexao.queryRegistro("SELECT minutos FROM usuario WHERE id={}".format(member.id))
                if(member.nick == None):                
                    await self.conexao.query("UPDATE usuario SET urlavatar = '{}', nome = '{}' WHERE id={}".format(member.avatar_url, member.name, member.id))
                else:
                    await self.conexao.query("UPDATE usuario SET urlavatar = '{}', nome = '{}' WHERE id={}".format(member.avatar_url, member.nick, member.id))
            else:
                if(member.nick == None):
                    await self.conexao.query("INSERT INTO usuario VALUES('{}','{}','{}', '{}')".format(member.id, member.name, "0", member.avatar_url))
                else:
                    await self.conexao.query("INSERT INTO usuario VALUES('{}','{}','{}', '{}')".format(member.id, member.nick, "0", member.avatar_url))
                self.fila_tempo[member.id] = 0
            try:
                while (before.channel is None) & (after.channel is not None):
                    await asyncio.sleep(60)
                    if len(after.channel.members) > 1:
                        await self.conexao.query("UPDATE usuario SET minutos=minutos+1 where id='{}'".format(member.id))
                    hora = datetime.now().astimezone(self.fuso_horario)
                    if (hora.hour == 0) and (hora.minute == 0):
                        await self.setar_horas(member.id, 1)
                        self.fila_tempo[member.id] = await self.conexao.queryRegistro("SELECT minutos FROM usuario WHERE id='{}'".format(member.id))
            except Exception as e:
                print('Exception = ' + e)
        else:
            await self.setar_horas(member.id, 0)
            del self.fila_tempo[member.id]

    async def setar_horas(self, user_id, flag):
        tempo_conectado = await self.conexao.queryRegistro("SELECT minutos FROM usuario WHERE id='{}'".format(user_id)) - self.fila_tempo[user_id]
        if(flag):
            data = datetime.today() - timedelta(days=1)
        else:
            data = datetime.now().astimezone(self.fuso_horario)
        if await self.conexao.queryRegistro("SELECT EXISTS(SELECT 1 FROM horas_diarias WHERE id_usuario='{}' AND data='{}')".format(user_id, data.strftime("%Y-%m-%d"))):
            await self.conexao.query("UPDATE horas_diarias SET minutos=minutos+{} where id_usuario='{}' AND data='{}'".format(tempo_conectado, user_id, data.strftime("%Y-%m-%d")))
        else:
            await self.conexao.query("INSERT INTO horas_diarias (id_usuario, data, minutos) VALUES('{}','{}','{}')".format(user_id, data.strftime("%Y-%m-%d"), tempo_conectado))

    @commands.command()
    async def rank(self, ctx):
        await ctx.send('Agora o rank está disponível em http://marmotexbotweb.herokuapp.com/')

    @commands.command()
    async def tempo(self, message, mentions: discord.Member = None):
        if mentions:
            await self.mostrarTempo(True, message, mentions)
        else:
            if await self.conexao.queryRegistro("SELECT EXISTS(SELECT 1 FROM usuario WHERE id={})".format(message.author.id)):
                await self.mostrarTempo(False, message, message.author)
            else:
                await message.send(message.channel, 'Você não tem horas registradas')


    async def mostrarTempo(self, flag, message, member):
        if flag:
            if await self.conexao.queryRegistro("SELECT EXISTS(SELECT 1 FROM usuario WHERE id={})".format(member.id)):
                result = await self.conexao.queryAll("SELECT nome, minutos, urlavatar FROM usuario WHERE id={}".format(member.id))
                embed = discord.Embed(
                    title='{}'.format(result[0][0]),
                    color=0x00ff00,
                    description='{}'.format(
                        timedelta(minutes=result[0][1]))[:-3]
                )
                if(result[0][2]):
                    embed.set_thumbnail(url="{}".format(result[0][2]))
                await message.send(message.channel, embed=embed)
            else:
                await message.send(message.channel, '{} não tem horas registradas'.format(member.nick))
        else:
            result = await self.conexao.queryAll("SELECT nome, minutos, urlavatar FROM usuario WHERE id={}".format(member.id))
            embed = discord.Embed(
                title='Olá,',
                color=0x00ff00,
                description=result[0][0] + '\nTempo conectado = {}'.format(
                    timedelta(minutes=result[0][1]))[:-3]
            )
            if(result[0][2]):
                    embed.set_thumbnail(url="{}".format(result[0][2]))
            await message.send(message.channel, embed=embed)


def setup(bot):
    bot.add_cog(HorasBot(bot))
