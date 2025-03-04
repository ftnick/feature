import discord
from discord.ext import commands
import time
import requests
import config
import sys
from modules._LoggerModule import setup_logging

logger = setup_logging(__name__)
logger.debug(f"imported, id: {id(sys.modules[__name__])}")


def main(bot):
    @bot.command(name="hoststatus", help="Shows host status.")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def status(ctx):
        FLY_API_TOKEN = config.API_TOKEN
        if not FLY_API_TOKEN:
            await ctx.reply("Error: FLY_API_TOKEN is not set in the json file.")
            return

        headers = {"Authorization": f"Bearer {FLY_API_TOKEN}"}
        try:
            response = requests.get(
                "https://api.machines.dev/v1/apps/feature/machines", headers=headers
            )
            response.raise_for_status()  # Raise an exception for HTTP errors
            app_status = response.json()
        except requests.RequestException as e:
            await ctx.reply(f"Error: Unable to fetch status. {str(e)}")
            return

        if not app_status or not isinstance(app_status, list):
            await ctx.reply("Error: Invalid API response.")
            return

        status_data = app_status[0]  # Adjust based on API response
        state = status_data.get("state", "unknown").capitalize()
        region = status_data.get("region", "unknown").upper()

        embed = discord.Embed(
            title="Host Status",
            description=f"State: {state}",
            color=(
                discord.Color.green()
                if state.lower() == "started"
                else discord.Color.red()
            ),
        )

        start_time = time.time()  # Start measuring time
        temp_msg = await ctx.reply("Sending ping request...")
        end_time = time.time()

        bot_latency = round(bot.latency * 1000, 2)  # WebSocket latency in ms
        api_latency = round((end_time - start_time) * 1000, 2)  # Round-trip time

        embed.add_field(name="Region", value=region, inline=True)
        embed.add_field(
            name="WebSocket Latency", value=f"{bot_latency} ms", inline=True
        )
        embed.add_field(
            name="API Response Time", value=f"{api_latency} ms", inline=True
        )

        embed.set_footer(
            text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar.url
        )

        await temp_msg.edit(content=None, embed=embed)
