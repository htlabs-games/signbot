import discord
from discord.ui import View, Button
from discord.ext import commands

class Paginator(View):
    """
    a paginator i guess
    """

    def __init__(self, timeout: int = 180, show_counter: bool = True):
        super().__init__(timeout=timeout)

        self.current = 0
        self.pages = None
        self.total = 0

        self.previous_button = Button(style=discord.ButtonStyle.primary,emoji=discord.PartialEmoji(name="\U000025c0"))
        self.next_button = Button(style=discord.ButtonStyle.primary, emoji=discord.PartialEmoji(name="\U000025b6"))
        self.ephemeral = False
        self.ctx = None
        self.message = None
        self.counter = None
        self.show_counter = show_counter

    async def start(self, ctx: discord.Interaction | commands.Context, pages: list[discord.Embed], ephemeral: bool = False):
        if isinstance(ctx, discord.Interaction):
            ctx = await commands.Context.from_interaction(ctx)

        self.pages = pages
        self.total = len(pages)

        self.previous_button.callback = self.previous
        self.next_button.callback = self.next

        self.add_item(self.previous_button)

        if self.show_counter:
            self.counter = Button(
                label=f"{self.current + 1}/{self.total}",
                style=discord.ButtonStyle.secondary,
                disabled=True
            )
            self.add_item(self.counter)

        self.add_item(self.next_button)

        self.ephemeral = ephemeral
        self.ctx = ctx
        self.message = await ctx.send(embed=self.pages[self.current], view=self, ephemeral=self.ephemeral)

    async def previous(self, interaction: discord.Interaction):
        if interaction.user != self.ctx.author:
            return await interaction.response.send_message(
                content="You cannot control this paginator because you did not execute it.",
                ephemeral=True
            )

        self.current = self.current - 1 % self.total
        if self.counter:
            self.counter.label = f"{self.current + 1}/{self.total}"

        await interaction.response.defer()
        await self.message.edit(embed=self.pages[self.current], view=self)

    async def next(self, interaction: discord.Interaction):
        if interaction.user != self.ctx.author:
            return await interaction.response.send_message(
                content="You cannot control this paginator because you did not execute it.",
                ephemeral=True
            )

        self.current = self.current + 1 % self.total
        if self.counter:
            self.counter.label = f"{self.current + 1}/{self.total}"

        await interaction.response.defer()
        await self.message.edit(embed=self.pages[self.current], view=self)

    async def on_timeout(self):
        for child in self.children:
            if isinstance(child, Button):
                child.disabled = True
        
        await self.message.edit(embed=self.pages[self.current], view=self)
        return await super().on_timeout()