import asyncio
import aiohttp
import discord
import logging

from discord.ext import commands

from os import getenv
from signbot.bot import SignBot
from signbot.paginator import Paginator

BASE_URL = getenv("BASE_URL")
NEWEST_URL = BASE_URL + "/api/get-frontpage/?data-category=newest"
LIMIT = 30

class Levels(commands.Cog):
    def __init__(self, bot: SignBot):
        self.bot = bot
        self.http_session = aiohttp.ClientSession(timeout=30)

    @commands.command(
        name="newest",
        description="Gets the newest published levels"
    )
    async def newest(self, ctx: commands.Context):
        await ctx.channel.typing()

        try:
            async with self.http_session.get(NEWEST_URL) as response:
                content = await response.json()
                if not "newest" in content:
                    raise ValueError("Received data is invalid.")
                
                levels: list[dict] = content["newest"][:LIMIT]
                embeds = list[discord.Embed] = []

                for level in levels:
                    embed = discord.Embed(
                        title=level["name"][:256] or "Untitled Level",
                        description=level["description"][:4096] or "No description provided",
                        url=f"{BASE_URL}/aroundtown/play?l={level["id"]}",
                        colour=discord.Colour.teal()
                    )

                    embed.set_author(name=level["author"])
                    if "thumbnail" in level:
                        embed.set_image(url=BASE_URL + level["thumbnail"])

                    embeds.append(embed)

                paginator = Paginator(show_counter=True)
                paginator.start(ctx, embeds)
                
        except ValueError as e:
            ctx.reply(content="The server returned invalid data. Try again in a moment.")
            logging.error(e)

        except asyncio.TimeoutError:
            ctx.reply(content="Sorry, the request timed out. Try again in a moment.")
            logging.error("Newest levels request timed out.")

async def setup(bot: SignBot):
    cog = Levels(bot)
    await bot.add_cog(cog)