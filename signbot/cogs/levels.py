import asyncio
import aiohttp
import discord
import logging

from discord.ext import commands

from os import getenv
from signbot.bot import SignBot
from signbot.paginator import Paginator

SERVER_URL = getenv("SERVER_URL")
NEWEST_URL = SERVER_URL + "/api/get-frontpage/?data-category=newest"
LIMIT = 30

class Levels(commands.Cog):
    def __init__(self, bot: SignBot):
        self.bot = bot
        self.http_session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(30))

    @commands.command(
        name="newest",
        description="Gets the newest published levels"
    )
    async def newest(self, ctx: commands.Context):
        await ctx.channel.typing()

        try:
            async with self.http_session.get(NEWEST_URL, headers={"Accept-Encoding": "gzip, deflate"}) as response:
                content = await response.json()
                if not "newest" in content:
                    raise ValueError("Received data is invalid.")
                
                levels: list[dict] = content["newest"][:LIMIT]
                embeds = []

                for level in levels:
                    embed = discord.Embed(
                        title=level["name"][:256] or "Untitled Level",
                        description=level["description"][:4096] or "No description provided",
                        url=f"{SERVER_URL}/aroundtown/play?l={level["id"]}",
                        colour=discord.Colour.teal()
                    )

                    embed.set_author(name=level["author"])
                    if level["thumbnail"] is not None:
                        embed.set_image(url=(SERVER_URL + level["thumbnail"]))

                    embeds.append(embed)

                paginator = Paginator(show_counter=True)
                await paginator.start(ctx, embeds)
                
        except ValueError as e:
            ctx.reply(content="The server returned invalid data. Try again in a moment.")
            logging.error(e)

        except asyncio.TimeoutError:
            ctx.reply(content="Sorry, the request timed out. Try again in a moment.")
            logging.error("Newest levels request timed out.")

async def setup(bot: SignBot):
    cog = Levels(bot)
    await bot.add_cog(cog)