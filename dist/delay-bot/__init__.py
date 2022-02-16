import aiohttp
import asyncio
import json

import twitchio.ext.commands
from twitchio.ext import commands


class Bot(commands.Bot):

    def __init__(self, delay_bot):
        # Initialise our Bot with our access token, prefix and a list of channels to join on boot...
        super().__init__(token=delay_bot.config['token'], prefix='!', initial_channels=[delay_bot.config['channel']])
        self.delay_bot = delay_bot

    async def event_ready(self):
        # We are logged in and ready to chat and use commands...
        print(f'Logged in as | {self.nick}')

    async def event_command_error(self, context, error):
        if isinstance(error, twitchio.ext.commands.CommandNotFound):
            return

        raise error

    @commands.command()
    async def delay(self, ctx: commands.Context):
        if 'broadcaster/1' in ctx.message.tags['badges'] or ctx.message.tags['mod'] == "1":
            args = ctx.message.content.split(" ", 3)
            try:
                source_idx = int(args[1])
            except (ValueError, IndexError):
                return

            offset = 0
            try:
                if args[2] == "an" or args[2] == "on":
                    offset = self.delay_bot.config['delay'] * 1000 * 1000
            except IndexError:
                return

            try:
                source = self.delay_bot.config['sources'][source_idx - 1]
            except IndexError:
                return

            await self.delay_bot.obs.send_json({"request-type": "SetSyncOffset",
                                                "source": source,
                                                "offset": offset,
                                                "message-id": "SetSync"})
            await asyncio.sleep(1)
            await self.delay_bot.obs.send_json({"request-type": "SetSyncOffset",
                                                "source": source,
                                                "offset": offset+1,
                                                "message-id": "SetSync"})

            # Send a hello back!
            await ctx.send(f'@{ctx.author.name} Delay gesetzt!')


class DelayBot:
    def __init__(self):
        self.session = aiohttp.ClientSession()
        self.obs = None
        self.bot = None

        with open("config.json") as config_file:
            self.config = json.load(config_file)

    async def run_bot(self):
        try:
            self.bot = Bot(self)
            await self.bot.connect()

            # run forever
            while True:
                await asyncio.sleep(3600)
        except asyncio.CancelledError:
            await self.bot.close()
            return

    async def obs_websocket(self):
        async with self.session.ws_connect('http://127.0.0.1:4444/') as self.obs:
            # run forever
            try:
                while True:
                    await asyncio.sleep(3600)
            except asyncio.CancelledError:
                return


async def main():
    db = DelayBot()
    await asyncio.gather(*[db.run_bot(), db.obs_websocket()])


def run():
    asyncio.run(main())


if __name__ == '__main__':
    run()
