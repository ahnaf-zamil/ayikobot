# Copyright (C) 2021 K.M Ahnaf Zamil

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


def human_format(num: int) -> str:
    """Converts an integer to a human-readable number format"""
    mag = 0
    while abs(num) >= 1000:
        num /= 1000
        mag += 1
    return f"{num:.1f}".rstrip("0").rstrip(".") + ["", "k", "M", "B", "T"][mag]
