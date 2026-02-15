import logging
import os
import sys
from dotenv import load_dotenv
from signbot.bot import SignBot

load_dotenv()

if __name__ == "__main__":
    bot = SignBot()

    try:
        bot.run(os.getenv("TOKEN"))
    except KeyboardInterrupt:
        logging.info("Interruption detected, shutting down gracefully...")
        bot.close()
    except Exception as e:
        logging.fatal(e)
        sys.exit(1)

    sys.exit(0)
    