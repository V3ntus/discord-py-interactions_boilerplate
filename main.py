"""
Main script to run

This script initializes cogs and starts the bot

Code taken from my contributions in:
https://github.com/savioxavier/repo-finder-bot/
Additional thanks to savioxavier
"""
import os
import sys

import interactions
from dotenv import load_dotenv
from interactions import MISSING

from config import DEBUG, DEV_GUILD
from src import logutil

load_dotenv()

# Configure logging for this main.py handler
logger = logutil.init_logger("main.py")
logger.debug(
    "Debug mode is %s; This is not a warning, \
just an indicator. You may safely ignore",
    DEBUG,
)

# Instantiate environment variables
TOKEN = None
try:
    if not (TOKEN := os.environ.get("TOKEN")):
        TOKEN = None
    if not DEV_GUILD or (DEV_GUILD := int(os.environ.get("DEV_GUILD"))):
        DEV_GUILD = MISSING
except TypeError:
    pass
finally:
    if TOKEN is None:
        logger.critical("TOKEN variable not set. Cannot continue")
        sys.exit(1)

client = interactions.Client(token=TOKEN, disable_sync=True)


# BEGIN on_ready
@client.event
async def on_ready():
    """Called when bot is ready to receive interactions"""

    # globalize this so the user may be able to use it later on
    global bot_user
    bot_user = interactions.User(**await client._http.get_self())

    logger.info("Logged in as %s#%s" % (bot_user.username, bot_user.discriminator))


# END on_ready


# BEGIN cogs_dynamic_loader
# Fill this array with Python files in /cogs.
# This omits __init__.py, template.py, and excludes files without a py file extension
cogs = [
    module[:-3]
    for module in os.listdir(f"{os.path.dirname(__file__)}/cogs")
    if module not in ("__init__.py", "template.py") and module[-3:] == ".py"
]

if cogs or cogs == []:
    logger.info("Importing %s cogs: %s", len(cogs), ", ".join(cogs))
else:
    logger.warning("Could not import any cogs!")

for cog in cogs:
    try:
        client.load("cogs." + cog)
    except Exception:  # noqa
        logger.error("Could not load a cog: {}".format(cog), exc_info=DEBUG)

# END cogs_dynamic_loader

client.start()
