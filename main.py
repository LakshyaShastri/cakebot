"""
    Cakebot - A cake themed Discord bot
    Copyright (C) 2019-current year  Reece Dunham

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import discord
import sys
from os import getenv
from logging import getLogger, StreamHandler
from filehandlers import AbstractFile, FileManipulator
from github import enable_console_debug_logging, Github
from area4 import divider
from fbootstrap import bootstrap
from reverse_geocoder import search
from discord.utils import oauth_url
from slots import row, result
from iss import Imp as ISSimp
from factdata import FactImp
from random import randint, choice
from requests import get
from bs4 import BeautifulSoup as Bs4
from lcpy import false
from club.cakebot import (
    TextCommandsUtil, EmbedUtil, UserUtil, Preconditions
)
from cookiescb import Cookies


logger = getLogger(__name__)
logger.setLevel(20)
logger.addHandler(StreamHandler(sys.stdout))


j = open("tokens.txt", mode="r").readlines()
for i, l in enumerate(j):
    j[i] = j[i].replace("\n", "")


AbstractFile("servers.txt").touch()
servers = FileManipulator(AbstractFile("servers.txt"))
AbstractFile("cookies.json").touch()

idk = open("cookies.json", "r")
if idk.read() == "":
    open("cookies.json", "w").write('{"players": []}')
idk.close()

enable_console_debug_logging()
g = None
try:
    g = Github(j[1])
except IndexError:
    logger.warning("GitHub credentials not found, skipping initialization...")

client = discord.AutoShardedClient()


def update_servers():
    bootstrap(client, servers)
    servers.refresh()


@client.event
async def on_ready():
    update_servers()
    if getenv("PRODUCTION") is not None:
        await client.change_presence(
            activity=discord.Game(
                name=open(
                    "content/status.txt",
                    "r"
                ).readlines()[0]
            )
        )
    else:
        await client.change_presence(
            activity=discord.Game(
                name="Running development build"
            )
        )
    logger.info("Ready to roll, I'll see you on Discord: @" + str(client.user))


@client.event
async def on_message(message):
    Bot_Prefix = "+"
    if getenv("PRODUCTION") is None:
        Bot_Prefix = "-"

    if not message.content.startswith(Bot_Prefix):
        return

    # Split input
    args = message.content[len(Bot_Prefix):].split()

    cmd = args[0].lower()

    # the arg array ex. ["hello", "world"]
    args = args[1:]

    s = message.channel.send

    if (
        (
            cmd == "8"
            or cmd == "report"
            or cmd == "define"
            or cmd == "stars"
            or cmd == "homepage"
            or cmd == "clapify"
            or cmd == "cookie"
        ) and Preconditions.checkArgsAreNotNull(
            args
        )
    ):
        return await s(
            embed=EmbedUtil.prep(
                "That command expected an argument (or arguments), but you didn't give it any!",
                "[Read the docs?](https://cakebot.club/commands.html)"
            )
        )

    if cmd == "help":
        return await s(embed=EmbedUtil.help_menu())

    elif cmd == "ping":
        return await s("🏓")

    elif cmd == "invite":
        return await s(
            embed=EmbedUtil.prep(
                "Invite Cakebot",
                f"[Click here to invite me!]({oauth_url(580573141898887199, permissions=discord.Permissions.all())})"
            )
        )

    elif cmd == "8":
        return await s(
            embed=EmbedUtil.prep(
                "**" + TextCommandsUtil.common("8ball") + "**",
                str(divider(7) + divider(7) + divider(7))
            )
        )

    elif cmd == "joke":
        return await s(
            embed=EmbedUtil.prep(
                f'**{TextCommandsUtil.common("jokes")}**', f'{divider(7)}{divider(7)}'
            )
        )

    elif cmd == "info":
        needs_mfa = bool(message.guild.mfa_level == 1)
        return await s(
            str(
                f'***{message.guild.name}***\n' +
                f'**Owner:** {message.guild.owner}\n' +
                f'**Members:** {len(message.guild.members)}\n' +
                f'**Region:** {message.guild.region}\n' +
                f'**Server ID:** {message.guild.id}\n' +
                f'**Nitro Booster Count:** {message.guild.premium_subscription_count}\n' +
                f'**Icon Is Animated:** {str(message.guild.is_icon_animated())}\n' +
                f'**Created At:** {str(message.guild.created_at)}\n' +
                f'**More Than 250 Members:** {str(message.guild.large)}\n' +
                f'**Admins Need 2-Factor Auth: {needs_mfa}'
            )
        )

    elif cmd == "report":
        repo = g.get_repo("cakebotpro/cakebot")
        String = ""
        for e, z in enumerate(args):  # noqa
            args[e] = str(args[e]) + " "
        f = str(String.join(args))
        if(f == "" or f == " "):
            return await s(":x: **I can't report nothing!**")
        repo.create_issue(
            title="Support ticket #" + str(randint(0, 100000)),
            body=str(
                f"## Support Ticket\n> Filed by {str(message.author)}\n### Message:\n`{f}`\n##### Powered by Cakebot | https://cakebot.club"
            ),
            labels=[
                repo.get_label("ticket")
            ]
        )
        return await s(":white_check_mark: **Our team has been notified.**")

    elif cmd == "iss":
        m = await s("Calculating...")
        imp = ISSimp()
        lat = imp.lat()
        lon = imp.lon()
        geodata = search((lat, lon))
        location = "{0}, {1}".format(geodata[0]["admin1"], geodata[0]["cc"])

        await m.delete()
        return await s(
            embed=EmbedUtil.prep(
                "International Space Station", "Where it is right now!"
            ).add_field(
                name="Location above Earth", value=str(location), inline=false
            ).add_field(
                name="Latitude", value=str(lat), inline=false
            ).add_field(
                name="Longitude", value=str(lon), inline=false
            )
        )

    elif cmd == "fact":
        return await s(embed=EmbedUtil.prep("Random Fact", FactImp().fact()))

    elif cmd == "slots":
        slotz = result()
        top = row()
        btm = row()
        form = "lose"
        if slotz[0] != 0:
            form = "win"
        return await s(
            f"⠀{top[0]}{top[1]}{top[2]}\n"
            # the line above contains unicode, DO NOT REMOVE
            + f"**>** {slotz[1][0]}{slotz[1][1]}{slotz[1][2]} **<**\n"
            + f"   {btm[0]}{btm[1]}{btm[2]}"
            + f"\n**You {form}!**"
        )

    elif cmd == "define":
        c = ""
        if len(args) < 1:
            return await s(":x: *You need to specify a word!*")
        if len(args) > 1:
            for b, h in enumerate(args):
                c = str(c + args[b] + "%20")
        else:
            c = args[0]
        sm = Bs4(get(f"https://www.merriam-webster.com/dictionary/{c}").content, "html.parser").find(
            "span", attrs={"class": "dtText"}
        ).text
        return await s(c + sm)

    elif cmd == "reboot":
        if str(message.author) in UserUtil.contributors():
            await s("Restarting. *This may take up to 5 minutes*.")
            # make the bot crash, forcing our server to turn it back on
            sys.exit(1)
        else:
            return await s(":x: **You are not authorized to run this!**")

    elif cmd == "pi":
        return await s(
            "3.14159265358979323846264338327950288419716939937510582097494459230781640628620899862803482534211706798214808651328230664709"
        )

    elif cmd == "coinflip":
        return await s(choice(["**Heads**.", "**Tails**."]))

    elif cmd == "stars":
        try:
            return await s(f"`{args[0]}` has *{g.get_repo(args[0]).stargazers_count}* stars.")
        except:
            return await s("Failed to get count. Is the repository valid and public?")

    elif cmd == "homepage":
        try:
            url_nullable = g.get_repo(args[0]).homepage
            if url_nullable is None:
                url_nullable = "(error: homepage not specified by owner)"
            return await s(f"{args[0]}'s homepage is located at {url_nullable}")
        except:
            return await s("Failed to fetch homepage. Is the repository valid and public?")

    elif cmd == "clapify":
        return await s(embed=EmbedUtil.prep(TextCommandsUtil.clapify(args), ""))

    elif cmd == "boomer":
        await s("Okay BOOMER!")
        return await s(file=discord.File("content/boomer.jpeg"))

    elif cmd == "cookie" or cmd == "cookies":
        cookies = Cookies("cookies.json")
        subcommand = args[0]
        if subcommand == "balance" or subcommand == "bal":
            user = message.author.id
            cy = TextCommandsUtil.get_mentioned_id(args)
            if cy is not None:
                user = cy
            return await s(cookies.get_count(user))
        elif subcommand == "give" or subcommand == "to":
            if cookies.give(TextCommandsUtil.get_mentioned_id(args)):
                return await s(":white_check_mark: *Cookie given!*")
            return await s(":x: *This user has already recieved a cookie in the last hour!*")


@client.event
async def on_guild_join(guild):
    update_servers()


@client.event
async def on_guild_remove(guild):
    update_servers()


@client.event
async def on_guild_update(before, after):
    update_servers()


if __name__ == "__main__":
    logger.info(f"Using discord.py version {discord.__version__}")
    client.run(j[0])
