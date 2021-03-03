from ayiko.client import Ayiko

import logging

# setting up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s[%(lineno)d] - %(levelname)s: %(message)s",
    datefmt="%m/%d/%y %H:%M:%S",
)

bot = Ayiko()

bot.run()
