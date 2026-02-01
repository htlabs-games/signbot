import discord
import asyncio
import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md

TOKEN = ""
CHANNEL_NAME = "📰-newsletter"
URL = "https://www.odysea.us.to/announcements/announcements.shtml"
CHECK_FREQ = 60 # announcements check frequency in seconds

intents = discord.Intents.default()
client = discord.Client(intents=intents)

last_h1_text = None


async def fetch_page():
    try:
        resp = requests.get(URL, timeout=10)
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
            content = content[:1400] + "\n...[read more](https://odysea.us.to/announcements)..."

        return first_h1, content

    except Exception as e:
        print(f"Error fetching page: {e}")
        return None, None


async def monitor_announcements():
    global last_h1_text
    global CHECK_FREQ
    await client.wait_until_ready()

    # initial check to prevent firing as soon as the bot starts up
    first_h1, content = await fetch_page()
    last_h1_text = first_h1
  
    while not client.is_closed():
        first_h1, content = await fetch_page()

        if first_h1 and first_h1 != last_h1_text:
            last_h1_text = first_h1
            channel = discord.utils.get(client.get_all_channels(), name=CHANNEL_NAME)
            if channel:
                msg = f"<@&1405506815847956540>\n# {first_h1}\n\n{content}" if content else f"**{first_h1}**"
                await channel.send(msg)

        await asyncio.sleep(CHECK_FREQ)


@client.event
async def on_ready():
    print(f"Logged in and ready to [SIGNBOT] as {client.user}")
    client.loop.create_task(monitor_announcements())


client.run(TOKEN)
