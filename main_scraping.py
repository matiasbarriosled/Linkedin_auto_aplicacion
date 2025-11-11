import os
from dotenv import load_dotenv

load_dotenv("secrets.env")

LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL")  
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")