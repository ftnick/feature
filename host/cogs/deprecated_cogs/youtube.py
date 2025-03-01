from discord.ext import commands
import discord
import os
import time
from yt_dlp import YoutubeDL
from modules._ReplyModule import reply
from modules._LoggerModule import setup_logging
import sys

logger = setup_logging(__name__)
logger.debug(f"imported, id: {id(sys.modules[__name__])}")

def main(bot):
    @bot.command(
        name="downloadytvideo",
        help="Download a youtube video onto a .mp4 file.",
        aliases=["dytv"],
    )
    @commands.cooldown(1, 60, commands.BucketType.guild)
    async def downloadytvideo(ctx, video_url: str):
        os.remove("videos/video.mp4") if os.path.exists("videos/video.mp4") else None
        start_time = time.time()  # Record start time
        try:
            with YoutubeDL({"outtmpl": "./videos/video.mp4", "format": "mp4"}) as ydl:
                ydl.download([f"{video_url}"])
        except Exception as e:
            logger.exception(e)
        finally:
            if os.path.exists("videos/video.mp4"):
                elapsed_time = time.time() - start_time
                upload_file = discord.File("videos/video.mp4", filename="video.mp4")
                await ctx.reply(
                    content=None,
                    file=upload_file,
                    embed=reply(ctx, f"Finished in {elapsed_time:.2f} seconds"),
                )
                os.remove("videos/video.mp4")
