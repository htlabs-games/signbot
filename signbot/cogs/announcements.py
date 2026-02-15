import asyncio
import discord
import logging
import requests
from bs4 import BeautifulSoup
from discord.ext import commands
from markdownify import markdownify as md
from os import getenv
from signbot.bot import SignBot

CHANNEL_ID = getenv("CHANNEL_ID")
SERVER_URL = getenv("SERVER_URL")
ANNOUNCEMENTS_URL = SERVER_URL + "/announcements/announcements.shtml"
CHECK_FREQ = getenv("CHECK_FREQ") or 60 # announcements check frequency in seconds

class Announcements(commands.Cog):
    def __init__(self, bot: SignBot):
        self.bot = bot
        self.bot.loop.create_task(self.monitor_announcements())

    async def fetch_page(self):
        try:
            resp = requests.get(ANNOUNCEMENTS_URL, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            # find all headers
            h1s = soup.find_all("h1")
            if not h1s:
                return None, None

            first_h1 = h1s[0].get_text(strip=True)

            # grab everything before second h1
            content_parts = []
            for elem in soup.find("h1").next_siblings:
                if getattr(elem, "name", None) == "h1":
                    break
                if hasattr(elem, "prettify"):
                    content_parts.append(str(elem))

            raw_html = "".join(content_parts)
            content = md(raw_html, strip=[])

            # format for discord
            if len(content) > 1400:  
                content = content[:1400] + f"\n...[read more]({SERVER_URL}/announcements)..."

            return first_h1, content
        except Exception as e:
            logging.error(f"Error fetching page: {e}")
            return None, None

    async def monitor_announcements(self):
        global last_h1_text
        await self.bot.wait_until_ready()

        # initial check to prevent firing as soon as the bot starts up
        first_h1, content = await self.fetch_page()
        last_h1_text = first_h1
    
        while not self.bot.is_closed():
            first_h1, content = await self.fetch_page()

            if first_h1 and first_h1 != last_h1_text:
                last_h1_text = first_h1
                channel = discord.utils.get(self.bot.get_all_channels(), id=CHANNEL_ID)
                if channel:
                    msg = f"<@&1405506815847956540>\n# {first_h1}\n\n{content}" if content else f"**{first_h1}**"
                    await channel.send(msg)

            await asyncio.sleep(int(CHECK_FREQ))

async def setup(bot: SignBot):
    cog = Announcements(bot)
    await bot.add_cog(cog)