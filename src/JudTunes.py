"""
Dev Bot Invite Link: https://discord.com/api/oauth2/authorize?client_id=925882289978757200&permissions=139690606144&scope=bot
Production Bot Invite Link:
"""

import discord
import os

from discord.ext import commands
from YouTube import YTDLSource


class JudTunes(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def join(self, ctx):
        if not ctx.message.author.voice:
            await ctx.send(f"{ctx.message.author.name} is not connected to a voice channel.")
            return
        else:
            channel = ctx.message.author.voice.channel
        await channel.connect()

    @commands.command()
    async def leave(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client:
            if voice_client.is_connected():
                await voice_client.disconnect()
            else:
                await ctx.send("The bot is not connected to a voice channel.")
        else:
            await ctx.send("The bot is not connected to a voice channel.")

    @commands.command(name='play', help='To play song')
    async def play(self, ctx, *url):

        # Combine search terms
        url = " ".join(url)

        if not url:
            # Try to unpause the previously playing song if no URL was given
            if ctx.voice_client and ctx.voice_client.is_paused():
                ctx.voice_client.resume()
            else:
                await ctx.send("No song was provided and nothing was playing before. Please provide a URL or "
                               "song title after the #play command")
        else:
            # Try to play the song
            try:
                async with ctx.typing():
                    player = await YTDLSource.from_url(url, loop=bot.loop, stream=True)
                    ctx.voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)
                await ctx.send('**Now playing:** {}'.format(player.title))
            except Exception as e:
                await ctx.send(f"Play error: {str(e)}")

    @commands.command(name='pause', help='This command pauses the song')
    async def pause(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
        else:
            await ctx.send("The bot is not playing anything at the moment.")

    @commands.command(name='resume', help='Resumes the song')
    async def resume(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()
        else:
            await ctx.send("The bot was not playing anything before this. Use the #play command.")

    @commands.command(name='stop', help='Stops the song')
    async def stop(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
        else:
            await ctx.send("The bot is not playing anything at the moment.")

    @play.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()


# Initialize bot, using the dev bot key if on Justin's computer
machine = os.environ['COMPUTERNAME']
bot = commands.Bot(command_prefix="#")
bot.add_cog(JudTunes(bot))


@bot.event
async def on_ready():
    print('Logged in as: ' + bot.user.name)

# Use dev version if on Justin's computer
if machine == "JUDTOP":
    bot.run('OTI1ODgyMjg5OTc4NzU3MjAw.YczlEw.nwWeoFD_KFZNvA2riGEqX6_MjHU')
else:
    bot.run('OTI1ODc5MDgxMDg0NTUxMTc4.YcziFg.m3mwGRE3KF_zsGridMtE-rWqpUk')
