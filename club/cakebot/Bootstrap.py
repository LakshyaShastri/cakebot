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

import area4


def bootstrap(c, s):
    # update servers
    for channel in c.get_all_channels():
        s.refresh()
        if channel.server.name not in s.get_cache():
            s.get_file().wrap().write(channel.server.name + "\n")
            s.refresh()

    # change RP
    await c.change_presence(game=discord.Game(name="Heya! Run +help", type=1))
    print(area4.divider(1))
    print("Ready to roll, I'll see you on Discord: @" + c.user.__str__())
    print(area4.divider(1))