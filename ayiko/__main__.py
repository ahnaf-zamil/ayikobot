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

from ayiko.client import Ayiko
from dotenv import load_dotenv

import logging

load_dotenv()

# setting up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s - %(levelname)s: %(message)s",
    datefmt="%m/%d/%y %H:%M:%S",
)

client = Ayiko()

client.run()
