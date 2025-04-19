from discord.ext import commands, tasks


class GameUpdate(commands.Cog):
    """
    GameUpdate Cog
    時間による更新処理をまとめるCog
    """
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.dec_fullness.start()

    @tasks.loop(hours=1)
    async def dec_fullness(self):
        """
        毎時間お腹が空きます
        """
        channel_ids = self.bot.database.get_habitat_channel_ids()
        for channel_id in channel_ids:
            self.bot.database.dec_fullness(channel_id, 2)
            print("おなかがすきました。")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(GameUpdate(bot))
