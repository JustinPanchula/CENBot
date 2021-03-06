__author__ = 'Justin Panchula'
__copyright__ = 'Copyright 2022'
__credits__ = 'Justin Panchula'
__license__ = 'MIT License'
__version__ = '1.0.0'
__status__ = 'Production'
__doc__ = """Logs messages and edits in discord servers"""

# Python imports
from pathlib import Path
import logging
import asyncio
from datetime import datetime
from http.client import HTTPException

# Discord imports
import discord
from discord.ext import commands

# Custom imports
from utils import JsonInteracts, get_id


class activitylog(commands.Cog):
    """These are all functions related to the activity log.
    """
    # Init
    def __init__(self, bot) -> None:
        self.bot = bot
        self.logchannelfile = Path('cogs/json files/loggingchannels.json')

        # Create file if it doesn't exist
        if not self.logchannelfile.is_file():
            self.logchannelfile.touch()

    # Check if loaded
    @commands.Cog.listener()
    async def on_ready(self):
        logging.info('Logging Cog loaded')

    # Choose log channel
    @commands.command(
        name='setlogchannel',
        brief='Chooses a channel to log information to',
        help='Chooses a channel to log information to'
    )
    @commands.has_role('Bot Manager')
    async def setlogchannel(self, ctx):
        # Init
        channels = JsonInteracts.Standard.read_json(self.logchannelfile)

        # Check if command user is giving input
        def checkuser(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel

        # Set new channel
        await ctx.send('What is the channel for message logging?')
        try:
            msg = await self.bot.wait_for('message', timeout=30.0, check=checkuser)
        except asyncio.TimeoutError:
            await ctx.send('Command has timed out')
        else:
            channels[str(ctx.guild.id)] = msg.content

        # Write to file
        JsonInteracts.Standard.write_json(self.logchannelfile, channels)

        # Send confirmation
        await ctx.send('Log channel set.')

    # Log message edits
    @commands.Cog.listener()
    async def on_message_edit(self, ctx_bef, ctx_aft):
        # Init
        channels = JsonInteracts.Standard.read_json(self.logchannelfile)

        # Get channel
        channel = self.bot.get_channel(get_id(channels[str(ctx_bef.guild.id)]))

        # Edited message embed
        embed = discord.Embed(colour=discord.Colour.gold())
        embed.set_author(name=ctx_bef.author.display_name, icon_url=ctx_bef.author.avatar_url)
        embed.add_field(name='Message Alert: Edit', value=f'A message sent by {ctx_bef.author.mention} was edited in {ctx_bef.channel.mention}\n[View Message]({ctx_aft.jump_url})', inline=False)
        # Ignore impossible message
        try:
            embed.add_field(name='Before', value=ctx_bef.content, inline=False)
        except discord.errors.HTTPException:
            return
        else:
            embed.add_field(name='After', value=ctx_aft.content, inline=False)
            embed.set_footer(text=f'{datetime.now().strftime("%d/%m/%y - %H:%M:%S")}')

        # Send to channel
        await channel.send(embed=embed)

    # Log message deletions
    @commands.Cog.listener()
    async def on_message_delete(self, ctx):
        # Init
        channels = JsonInteracts.Standard.read_json(self.logchannelfile)

        # Get channel
        channel = self.bot.get_channel(get_id(channels[str(ctx.guild.id)]))

        # Deleted message embed
        embed = discord.Embed(colour=discord.Colour.red())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        embed.add_field(name='Message Alert: Deletion', value=f'A message sent by {ctx.author.mention} was deleted in {ctx.channel.mention}', inline=False)
        # Ignore impossible message
        try:
            embed.add_field(name='Content', value=ctx.content)
        except discord.errors.HTTPException:
            return
        except HTTPException:
            return
        embed.set_footer(text=f'{datetime.now().strftime("%d/%m/%y - %H:%M:%S")}')

        # Send to channel
        await channel.send(embed=embed)


# Add to bot
def setup(bot) -> None:
    bot.add_cog(activitylog(bot))