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
