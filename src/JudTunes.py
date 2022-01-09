"""
Dev Bot Invite Link: https://discord.com/api/oauth2/authorize?client_id=925882289978757200&permissions=139690606144&scope=bot
Production Bot Invite Link:
"""

import discord
import asyncio
import socket
import sys
import os


from discord.ext import commands
from YouTube import YTDLSource


class JudTunes(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.playlist = asyncio.Queue()
        self.play_next_event = asyncio.Event()

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

    @commands.command(name='play', help='Play or resume a song')
    async def play(self, ctx, *track):
        """
        :param track: May be a series of space separated keywords for some song or a URL
        """
        # Combine search terms
        track = " ".join(track)

        if not track:
            # Try to unpause the previously playing song if no URL was given
            if ctx.voice_client and ctx.voice_client.is_paused():
                ctx.voice_client.resume()
            else:
                await ctx.send("No song was provided and nothing was playing before. Enter a URL or "
                               "song title after the #play command")
        else:
            try:
                player = await YTDLSource.from_url(track, loop=self.bot.loop, stream=True)
                ctx.voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)
                await ctx.send(f"**Now playing:** {player.title}")

            except Exception as e:
                await ctx.send(f"Play error: {str(e)}")

    # async def start_playing(self, vc):
    #
    #     while True:
    #         self.play_next_event.clear()
    #         print("Cleared event")
    #         player = await self.playlist.get()
    #         print("Got song")
    #         vc.play(player, after=lambda e: print(f'Player error: {e}') if e else self.play_next_event.set())
    #         # await ctx.send(f"**Now playing:** {player.title}")
    #         await self.play_next_event.wait()
    #         print("Event set")

    # @commands.command(name='playnext', help='This command adds a song to front of the queue')
    # async def play_next(self, ctx, *track):
    #
    #     # Combine search terms
    #     track = " ".join(track)
    #
    #     if ctx.voice_client:
    #
    #         if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
    #             self.playlist.insert(0, track)
    #             await ctx.send(f"Playing \"{track}\" next.")
    #         else:
    #             await self.play_audio(ctx, track)
    #
    #         if ctx.voice_client.is_paused():
    #             ctx.voice_client.resume()

    @commands.command(name='pause', help='Pause a song')
    async def pause(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
        else:
            await ctx.send("The bot is not playing anything at the moment.")

    # @commands.command(name='resume', help='Resumes the song')
    # async def resume(self, ctx):
    #     if ctx.voice_client and ctx.voice_client.is_paused():
    #         ctx.voice_client.resume()
    #     else:
    #         await ctx.send("The bot was not playing anything before this. Use the #play command.")

    @commands.command(name='stop', help='Stop a song')
    async def stop(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
        else:
            await ctx.send("The bot is not playing anything at the moment.")

    # @commands.command(name="add", help="Add a song to the end of the playlist")
    # async def add(self, ctx, *track):
    #     # Combine search terms
    #     track = " ".join(track)
    #     player = await YTDLSource.from_url(track, loop=self.bot.loop, stream=True)
    #     await self.playlist.put(player)
    #     await ctx.send(f"**Added:** {player.title}")

    # @commands.command(name="skip", help="Skips to the next song in the playlist")
    # async def skip(self, ctx):
    #     print(ctx.voice_client.is_playing())
    #     if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
    #         ctx.voice_client.stop()
    #         await ctx.send("Track skipped.")
    #         self.play_next_event.set()
    #     else:
    #         await ctx.send("Nothing playing to skip!")

    # @commands.command(name="clear", help="Clears the playlist")
    # async def clear(self, ctx):
    #     self.playlist.clear()
    #     await ctx.send("Tracklist cleared.")

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


# Get computer name and command line args
machine = socket.gethostname()
prod = len(sys.argv) > 1 and sys.argv[1] == "prod"

bot = commands.Bot(command_prefix="#")
bot.add_cog(JudTunes(bot))


@bot.event
async def on_ready():
    print('Logged in as: ' + bot.user.name)

# Use dev or prod version of bot
if prod:
    key = 'JudTunesKey'
else:
    key = 'JudTunesKeyDev'

KEY = os.environ.get(key)
if KEY is not None:
    bot.run(KEY)
else:
    # Log error here
    print(f"Could not run bot, no environment variable called {key}.")
