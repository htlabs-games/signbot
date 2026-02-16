import json
import logging
from discord.ext import commands

from os import getenv
from signbot.bot import SignBot

ALLOWED_ROLE = int(getenv("TESTERS_ROLE"))

class Admin(commands.Cog):
    def __init__(self, bot: SignBot):
        self.bot = bot

    @commands.command(
        name="whitelist",
        description="Adds or removes a username from the Alpha Vault whitelist",
    )
    @commands.has_role(ALLOWED_ROLE)
    async def whitelist(self, ctx: commands.Context, username: str):
        is_owner = await self.bot.is_owner(ctx.author)

        whitelist_path = getenv("WHITELIST_PATH")
        if whitelist_path is None or not len(whitelist_path.strip()):
            return await ctx.reply("There is not a whitelist json path set, please set the `WHITELIST_PATH` environment variable.")
        
        try:
            with open(whitelist_path, "r+", encoding="utf-8") as file:
                parsed: list[str] = json.loads(file.read())
                action = "removed from" if username in parsed else "added to"
                
                if username in parsed:
                    if is_owner:
                        parsed.remove(username)
                    else:
                        file.close()
                        return await ctx.reply("Only bot owners are allowed to remove usernames from the whitelist.")
                else:
                    parsed.append(username)

                file.seek(0)
                json.dump(parsed, file, indent=4)
                file.truncate()
                return await ctx.reply(f"Username `{username}` was successfully {action} the whitelist")
        except FileNotFoundError:
            return await ctx.reply("There whitelist json file was not found, make sure the `WHITELIST_PATH` environment variable is correct.")
        except Exception as e:
            logging.error(f"Failed to read whitelist JSON file: {e}")
            return await ctx.reply("An exception occured, check the console for details.")

async def setup(bot: SignBot):
    cog = Admin(bot)
    await bot.add_cog(cog)