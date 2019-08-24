import os
from dotenv import load_dotenv

load_dotenv()

databaseToken = os.getenv('DATABASE_URL')
discordToken = os.getenv('TOKEN')